#!/usr/bin/env python3
import sys
sys.path.append('../../src')

from parsers import parser
from exprs import expr_transforms
from verifiers import verifiers
from termsolvers import termsolvers
from eusolver_utils import lia_massager
from eusolver_utils import utils
from termsolvers import termsolvers_lia
from core import specifications
from unifiers import unifiers
from unifiers import unifiers_lia
from core import solvers
from exprs import exprs
from enumerators import enumerators
from exprs import exprtypes
from semantics import semantics_core
from core import grammars
from dsl import *
import signal
import os
from benchmarks import benchmarks
import time
import csv
import json


def handler(signum, frame):
    raise TimeOutException("Timeout")


class TimeOutException(Exception):
    def __init__(self, message, errors=None):
        super(TimeOutException, self).__init__(message)
        self.errors = errors


def get_pbe_valuations(constraints, synth_fun):
    valuations = []
    for constraint in constraints:
        if not exprs.is_application_of(constraint, 'eq') and \
                not exprs.is_application_of(constraint, '='):
            return None
        if len(exprs.get_all_variables(constraint)) > 0:
            return None
        arg_func, arg_other = None, None
        for a in constraint.children:
            if exprs.is_application_of(a, synth_fun):
                arg_func = a
            else:
                arg_other = a
        if arg_func is None or arg_other is None:
            return None
        valuations.append((arg_func.children, arg_other))
    return valuations

def massage_constraints(syn_ctx, macro_instantiator, uf_instantiator, theory, constraints):
    # Instantiate all macro functions
    constraints = [ macro_instantiator.instantiate_all(c)
            for c in constraints ]

    # for c in constraints:
    #     print(exprs.expression_to_string(c))
    # print('Ackermann Reduction')
    constraints = expr_transforms.AckermannReduction.apply(constraints, uf_instantiator, syn_ctx)
    # for c in constraints:
    #     print(exprs.expression_to_string(c))
    # print('let flattener')
    constraints = expr_transforms.LetFlattener.apply(constraints, syn_ctx)
    # for c in constraints:
    #     print(exprs.expression_to_string(c))
    # print('Rewrite ite')
    constraints = expr_transforms.RewriteITE.apply(constraints, syn_ctx)
    # for c in constraints:
    #     print(exprs.expression_to_string(c))
    # constraints, full_constraint_expr = expr_transforms.to_cnf(constraints, theory, syn_ctx)

    # Rewrite ITE?
    return constraints

def rewrite_solution(synth_funs, solution, reverse_mapping):
    # Rewrite any predicates introduced in grammar decomposition
    if reverse_mapping is not None:
        for function_info, cond, orig_expr_template, expr_template in reverse_mapping:
            while True:
                app = exprs.find_application(solution, function_info.function_name)
                if app is None:
                    break
                assert exprs.is_application_of(expr_template, 'ite')

                ite = exprs.parent_of(solution, app)
                ite_without_dummy = exprs.FunctionExpression(ite.function_info, (app.children[0], ite.children[1], ite.children[2]))
                var_mapping = exprs.match(expr_template, ite_without_dummy)
                new_ite = exprs.substitute_all(orig_expr_template, var_mapping.items())
                solution = exprs.substitute(solution, ite, new_ite)

    # Rewrite back into formal parameters
    if len(synth_funs) == 1:
        sols = [solution]
    else:
        # The solution will be a comma operator combination of solution 
        # to each function
        sols = solution.children

    rewritten_solutions = []
    for sol, synth_fun in zip(sols, synth_funs):
        variables = exprs.get_all_formal_parameters(sol)
        substitute_pairs = []
        orig_vars = synth_fun.get_named_vars()
        for v in variables:
            substitute_pairs.append((v, orig_vars[v.parameter_position]))
        sol = exprs.substitute_all(sol, substitute_pairs)
        rewritten_solutions.append(sol)

    return rewritten_solutions

def _merge_grammars(sf_grammar_list):
    start = "MergedStart"
    nts = [start]
    nt_type = {}
    rules = {}
    starts = []
    for sf_name, sf_obj, grammar in sf_grammar_list:
        renamed_grammar = grammar.add_prefix(sf_name)
        nts.extend(renamed_grammar.non_terminals)
        nt_type.update(renamed_grammar.nt_type)
        rules.update(renamed_grammar.rules)
        starts.append(renamed_grammar.start)
    comma_function = semantics_core.CommaFunction([ nt_type[s] for s in starts ])
    rules[start] = [ grammars.FunctionRewrite(comma_function,
            *tuple([ grammars.NTRewrite(s, nt_type[s]) for s in starts ])) ]
    nt_type[start] = None
    merged_grammar = grammars.Grammar(nts, nt_type, rules, start)

    return merged_grammar

def make_specification(synth_funs, theory, syn_ctx, constraints):
    if not expr_transforms.is_single_invocation(constraints, theory, syn_ctx):
        specification = specifications.MultiPointSpec(syn_ctx.make_function_expr('and', *constraints),
                syn_ctx, synth_funs)
        syn_ctx.set_synth_funs(synth_funs)
        verifier = verifiers.MultiPointVerifier(syn_ctx, specification)
    elif len(synth_funs) == 1 and get_pbe_valuations(constraints, synth_funs[0]) is not None:
        synth_fun = synth_funs[0]
        valuations = get_pbe_valuations(constraints, synth_fun)
        specification = specifications.PBESpec(valuations, synth_fun, theory)
        syn_ctx.set_synth_funs(synth_funs)
        verifier = verifiers.PBEVerifier(syn_ctx, specification)
    else:
        spec_expr = constraints[0] if len(constraints) == 1 \
                else syn_ctx.make_function_expr('and', *constraints)
        specification = specifications.StandardSpec(spec_expr, syn_ctx, synth_funs, theory)
        syn_ctx.set_synth_funs(synth_funs)
        verifier = verifiers.StdVerifier(syn_ctx, specification)
    return specification, verifier

def full_lia_grammars(grammar_map):
    massaging = {}
    for sf, grammar in grammar_map.items():
        full = False
        if grammar.from_default:
            full = True
        else:
            ans = grammars.identify_lia_grammars(sf, grammar)
            if ans is None:
                full = False
            else:
                massaging[sf] = ans
                full = True
        if not full:
            return False, None
    return True, massaging

class UnsuitableSolverException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[ERROR]: UnsuitableSolverException %s" % self.message

def lia_unification_solver(theory, syn_ctx, synth_funs, grammar_map, specification, verifier):
    if theory != 'LIA':
        raise UnsuitableSolverException('LIA Unification Solver: Not LIA theory')
    if any([sf.range_type != exprtypes.IntType() for sf in synth_funs ]):
        raise UnsuitableSolverException('LIA Unification Solver: Cannot handle bool return values yet')
    if not specification.is_pointwise():
        raise UnsuitableSolverException('LIA Unification Solver: Not pointwise spec')

    okay, massaging = full_lia_grammars(grammar_map) 
    if not okay:
        raise UnsuitableSolverException('LIA Unification Solver: Could not get LIA full grammar')

    term_solver = termsolvers_lia.SpecAwareLIATermSolver(specification.term_signature, specification)
    unifier = unifiers_lia.SpecAwareLIAUnifier(None, term_solver, synth_funs, syn_ctx, specification)
    solver = solvers.Solver(syn_ctx)
    solutions = solver.solve(
            enumerators.NullGeneratorFactory(),
            term_solver,
            unifier,
            verifier,
            verify_term_solve=False
            )
    solution = next(solutions)
    final_solution = rewrite_solution(synth_funs, solution, reverse_mapping=None)
    final_solution = lia_massager.massage_full_lia_solution(syn_ctx, synth_funs, final_solution, massaging)
    if final_solution is None:
        raise UnsuitableSolverException('LIA Unification Solver: Could not massage back solution')  
    return final_solution

def std_unification_solver(theory, syn_ctx, synth_funs, grammar_map, specification, verifier):
    if len(synth_funs) > 1:
        raise UnsuitableSolverException("DT Unification Solver: Multi-function unification not supported")
    if specification.is_multipoint:
        raise UnsuitableSolverException("Multi point specification")

    synth_fun = synth_funs[0]
    grammar = grammar_map[synth_fun]

    decomposed_grammar = grammar.decompose(syn_ctx.macro_instantiator)
    if decomposed_grammar == None:
        raise UnsuitableSolverException("DT Unification Solver: Unable to decompose grammar")
    term_grammar, pred_grammar, reverse_mapping = decomposed_grammar

    generator_factory = enumerators.PointDistinctGeneratorFactory(specification)
    term_generator = term_grammar.to_generator(generator_factory)
    pred_generator = pred_grammar.to_generator(generator_factory)
    solver = solvers.Solver(syn_ctx)
    term_solver = termsolvers.PointDistinctTermSolver(specification.term_signature, term_generator)
    unifier = unifiers.PointDistinctDTUnifier(pred_generator, term_solver, synth_fun, syn_ctx)
    solver = solvers.Solver(syn_ctx)
    solutions = solver.solve(
            generator_factory,
            term_solver,
            unifier,
            verifier,
            verify_term_solve=True
            )
    solution = next(solutions)
    final_solution = rewrite_solution([synth_fun], solution, reverse_mapping)
    return final_solution

def classic_esolver(theory, syn_ctx, synth_funs, grammar_map, specification, verifier):
    if len(synth_funs) != 1:
        raise UnsuitableSolverException("Classic esolver for multi-function disable due to bugs")
    assert len(synth_funs) == 1
    try:
        generator_factory = enumerators.PointDistinctGeneratorFactory(specification)
    except:
        raise UnsuitableSolverException("Enumerator problems")

    TermSolver = termsolvers.PointDistinctTermSolver
    grammar = grammar_map[synth_funs[0]]
    term_generator = grammar.to_generator(generator_factory)

    term_solver = TermSolver(specification.term_signature, term_generator)
    term_solver.stopping_condition = termsolvers.StoppingCondition.one_term_sufficiency
    unifier = unifiers.NullUnifier(None, term_solver, synth_funs, syn_ctx, specification)

    solver = solvers.Solver(syn_ctx)
    solutions = solver.solve(
            generator_factory,
            term_solver,
            unifier,
            verifier,
            verify_term_solve=False,
            )
    try:
        solution = next(solutions)
    except StopIteration:
        return "NO SOLUTION"
    rewritten_solutions = rewrite_solution(synth_funs, solution, reverse_mapping=None)
    return rewritten_solutions

def memoryless_esolver(theory, syn_ctx, synth_funs, grammar_map, specification, verifier):
    generator_factory = enumerators.RecursiveGeneratorFactory()
    TermSolver = termsolvers.PointlessTermSolver

    if len(synth_funs) > 1:
        sf_list = [ (synth_fun.function_name, synth_fun, grammar_map[synth_fun])
            for synth_fun in synth_funs ]
        grammar = _merge_grammars(sf_list)
    else:
        grammar = grammar_map[synth_funs[0]]

    term_generator = grammar.to_generator(generator_factory)

    term_solver = TermSolver(specification.term_signature, term_generator)
    term_solver.stopping_condition = termsolvers.StoppingCondition.one_term_sufficiency
    unifier = unifiers.NullUnifier(None, term_solver, synth_funs, syn_ctx, specification)

    solver = solvers.Solver(syn_ctx)
    solutions = solver.solve(
            generator_factory,
            term_solver,
            unifier,
            verifier,
            verify_term_solve=False
            )
    solution = next(solutions)
    rewritten_solutions = rewrite_solution(synth_funs, solution, reverse_mapping=None)
    return rewritten_solutions

def make_solver(file_sexp, id_to_text):
    benchmark_tuple = parser.extract_benchmark(file_sexp)
    (
            theories,
            syn_ctx,
            synth_instantiator,
            macro_instantiator,
            uf_instantiator,
            constraints,
            grammar_map,
            forall_vars_map
            ) = benchmark_tuple

    assert len(theories) == 1
    theory = theories[0]

    solvers = [
            ("LIA Unification", lia_unification_solver),
            ("STD Unification", std_unification_solver),
            ("Classic Esolver", classic_esolver),
            ("Memoryless Esolver", memoryless_esolver)
            ]
    rewritten_constraints = utils.timeout(
            massage_constraints,
            (syn_ctx, macro_instantiator, uf_instantiator, theory, constraints),
            {},
            timeout_duration=120,
            default=None
            )
    if rewritten_constraints is not None:
        constraints = rewritten_constraints
    else:
        solvers = [
            ("Memoryless Esolver", memoryless_esolver)
            ]
    synth_funs = list(synth_instantiator.get_functions().values())
    specification, verifier = make_specification(synth_funs, theory, syn_ctx, constraints)


    solver_args = (
            theory,
            syn_ctx,
            synth_funs,
            grammar_map,
            specification,
            verifier
            )
    for solver_name, solver in solvers:
        try:
            print("Trying solver:", solver_name)
            final_solutions = solver(*solver_args)
            if final_solutions == "NO SOLUTION":
                return "(fail)"
            else:
                return get_solutions(synth_funs, final_solutions, id_to_text)
            break
        except UnsuitableSolverException as exception:
            # print(exception)
            pass
    else:
        print("Unable to solve!")
        pass

constants = {"MouthOpen": MouthOpen(), 
            "EyesOpen": EyesOpen(), 
            "BelowAge18": BelowAge(18), 
            "Smile": IsSmiling(), 
            "IsPrice": IsPrice(),
            "IsPhoneNumber": IsPhoneNumber(), 
            "TypeFace": IsFace(), 
            "TypeText": IsText(),
            "GetLeft": GetLeft(), 
            "GetRight": GetRight(), 
            "GetAbove": GetAbove(), 
            "GetBelow": GetBelow(), 
            "GetNext": GetNext(), 
            "GetPrev": GetPrev(), 
            "GetChildren": GetContains(), 
            "GetParents": GetIsContained()}

def constant_to_prog(s, id_to_text):
    if s in constants:
        return constants[s]
    if s.startswith("Name"):
        return IsObject(s[4:].replace('1', ' '))
    if s.startswith("Text"):
        return MatchesWord(id_to_text[int(s[4:])])
    if s.startswith("Index"):
        return GetFace(int(s[5:]))

def expression_to_imgman2(expr, id_to_text):
    """Returns a string representation of an expression"""
    kind = expr.expr_kind
    if (kind == exprs._constant_expression):
        # print(expr.value_object.value_object)
        return constant_to_prog(expr.value_object.value_object, id_to_text)
    elif (kind == exprs._variable_expression):
        return 3
    else:
        # print(expr.function_info.function_name)
        children = []
        for child in expr.children:
            children.append(expression_to_imgman2(child, id_to_text))
        if expr.function_info.function_name == "Find":
            return Map(children[1], children[2], children[3])
        elif expr.function_info.function_name == "Match":
            return children[1]
        elif expr.function_info.function_name == "Complement":
            return Complement(children[1])
        elif expr.function_info.function_name == "Union":
            union_children = []
            for child in children:
                if isinstance(child, Union):
                    union_children += child.extractors
                else:
                    union_children.append(child)
            return Union(union_children)
        elif expr.function_info.function_name == "Intersect":
            inter_children = []
            for child in children:
                if isinstance(child, Intersection):
                    inter_children += child.extractors
                else:
                    inter_children.append(child)
            return Intersection(inter_children)

def get_solutions(synth_funs, final_solutions, id_to_text):
    for sf, sol in zip(synth_funs, final_solutions):
        fp_infos = []
        for v in sf.get_named_vars():
            v_name = v.variable_info.variable_name 
            v_type = v.variable_info.variable_type.print_string()
            fp_infos.append((v_name, v_type))
        prog = expression_to_imgman2(sol, id_to_text)
        print(prog)
        return prog
        # print(prog)
        # raise TypeError
        # fp_infos_strings = [ '(%s %s)' % (n, t) for (n, t) in fp_infos ]
        # fp_string = ' '.join(fp_infos_strings)

        # return '(define-fun {} ({}) {}\n     {})'.format(
        #         sf.function_name,
        #             fp_string,
        #             sf.range_type.print_string(),
        #             exprs.expression_to_string(sol)
                # )

# Tests:

def test_make_solver():
    directory = '../benchmarks/imgman/'
    data = []
    with open('imgman/example_imgs.json', 'r') as f:
        benchmark_to_example_imgs = json.load(f)
    with open('imgman/text_to_id.json', 'r') as f:
        text_to_id = json.load(f)
    for filename in os.listdir(directory):
        # for filename in ['imgman8.sl']:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)
        if len(filename) == 10:
            benchmark = benchmarks[int(filename[-4])]
            example_imgs = benchmark_to_example_imgs[filename[-4]]
        elif len(filename) == 11:
            benchmark = benchmarks[int(filename[-5:-3])]
            example_imgs = benchmark_to_example_imgs[filename[-5:-3]]
        benchmark_file = os.path.join(directory, filename)
        file_sexp = parser.sexpFromFile(benchmark_file)
        start_time = time.perf_counter()
        try:
            output = make_solver(file_sexp, text_to_id)
        except TimeOutException:
            row = (str(benchmark.gt_prog), "TIMEOUT")
            data.append(row)
            print("TIMEOUT")
            continue
        end_time = time.perf_counter()
        total_time = end_time - start_time
        row = (
            str(benchmark.gt_prog),
            output,
            benchmark.dataset_name,
            total_time,
            benchmark.desc,
            benchmark.ast_depth,
            benchmark.ast_size,
            len(benchmark.example_imgs),
            benchmark.example_imgs,
        )
        data.append(row)
    with open('results.csv', "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Ground Truth Prog",
                "Synthesized Prog",
                "Dataset",
                "Total Time",
                "Description",
                "AST Depth",
                "AST Size",
                "# Example Images",
                "Example Images"
            ),
        )
        for row in data:
            fw.writerow(row)

def test_make_solver2(filename, id_to_text):
    print(filename)
    directory = '../benchmarks/imgman/'
    data = []
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)
    # if len(filename) == 10:
    #     benchmark = benchmarks[int(filename[-4])]
    #     example_imgs = benchmark_to_example_imgs[filename[-4]]
    # elif len(filename) == 11:
    #     benchmark = benchmarks[int(filename[-5:-3])]
    #     example_imgs = benchmark_to_example_imgs[filename[-5:-3]]
    benchmark_file = os.path.join(directory, filename)
    file_sexp = parser.sexpFromFile(filename)
    start_time = time.perf_counter()
    try:
        output = make_solver(file_sexp, id_to_text)
    except TimeOutException:
        row = (str(benchmark.gt_prog), "TIMEOUT")
        print("TIMEOUT")
        return row
    end_time = time.perf_counter()
    total_time = end_time - start_time
    return output, total_time



if __name__ == "__main__":
    # import sys
    # benchmark_files = sys.argv[1:]
    # print(benchmark_files)
    test_make_solver()
