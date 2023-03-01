from interpreter import eval_extractor, get_environment, partial_eval, eval_apply_action
import heapq as hq
import itertools
import psutil
import random
import signal
from utils import *
from image_utils import *
from ordered_set import OrderedSet
from tkinter import *
from tkinter import filedialog


def get_prog_output(prog, env, parent):
    if (
        isinstance(prog, Union)
        or isinstance(prog, Intersection)
        or isinstance(prog, Complement)
        or isinstance(prog, Map)
        or isinstance(prog, MatchesWord)
        or isinstance(prog, GetFace)
        or isinstance(prog, IsObject)
        or isinstance(prog, AboveAge)
        or isinstance(prog, BelowAge)
    ):
        return None
    if isinstance(parent, MatchesWord):
        prog = MatchesWord(prog)
    elif isinstance(parent, GetFace):
        prog = GetFace(prog)
    elif isinstance(parent, IsObject):
        prog = IsObject(prog)
    elif isinstance(parent, AboveAge):
        prog = AboveAge(prog)
    elif isinstance(parent, BelowAge):
        prog = BelowAge(prog)
    return eval_extractor(prog, env)


def get_attributes(output_over, output_under, dataset=None):
    return [
        (IsFace(), [], [], [], 0),
        (IsText(), [], [], [], 0),
        (IsPrice(), [], [], [], 0),
        (IsPhoneNumber(), [], [], [], 0),
        (IsSmiling(), [], [], [], 0),
        (EyesOpen(), [], [], [], 0),
        (MouthOpen(), [], [], [], 0),
        (MatchesWord(None), ["word"], [output_over], [output_under], 1),
        (IsObject(None), ["obj"], [output_over], [output_under], 0),
        (GetFace(None), ["index"], [output_over], [output_under], 1),
        (BelowAge(18), [], [], [], 0),
    ]


def get_extractors(
    parent_extr: Extractor, output_over, output_under, env
) -> List[Extractor]:
    extrs = get_attributes(output_over, output_under)
    extrs += (
        (
            Complement(None),
            ["extr"],
            [set(env.keys()) - output_under],
            [set(env.keys()) - output_over],
            1,
        ),
    )
    if not isinstance(parent_extr, Union):
        for i in range(2, 4):
            extrs.append(
                (Union([None] * i), ["extr"] * i, [output_over] * i, [set()] * i, i)
            ),
    if not isinstance(parent_extr, Intersection):
        for i in range(2, 4):
            extrs.append(
                (
                    Intersection([None] * i),
                    ["extr"] * i,
                    [set(env.keys())] * i,
                    [output_under] * i,
                    i,
                )
            ),
    # map_weight = 5 if isinstance(parent_extr, Map) else 3
    map_weight = 3
    extrs += [
        (
            Map(None, None, pos),
            ["extr", "attr"],
            [set(env.keys()), set(env.keys())],
            [set(), output_under],
            map_weight,
        )
        for pos in get_positions()
    ]
    return extrs


class IOExample:
    def __init__(
        self,
        trace,
        img_dirs: List[str],
        client,
        gt_prog: str,
        explanation: str,
        max_faces: int,
        prev_env=None,
        img_to_environment=None,
    ):
        self.trace = trace
        self.img_dirs = img_dirs
        self.gt_prog = gt_prog
        self.explanation = explanation
        if img_to_environment:
            env = {}
            for img_dir in img_dirs:
                env = {**env, **img_to_environment[img_dir]["environment"]}
            self.env = env
        else:
            self.env = get_environment(
                img_dirs, client, DETAIL_KEYS, prev_env, max_faces
            )
        for details_map in self.env.values():
            if "ActionApplied" in details_map:
                del details_map["ActionApplied"]
        for action, l in trace.items():
            for (img_index, index) in l:
                for details_map in self.env.values():
                    if (
                        details_map["ObjPosInImgLeftToRight"] == index
                        and details_map["ImgIndex"] == img_index
                    ):
                        details_map["ActionApplied"] = action
        self.obj_list = self.env.keys()
        # dictionary from action to fta
        self.fta_by_action = {}
        # dictionary from action to state mapping
        self.state_to_forward_transitions_by_action = {}


class Tree:
    def __init__(self, _id: int):
        self.id: int = _id
        self.nodes: Dict[int, Extractor] = {}
        self.to_children: Dict[int, List[int]] = {}
        self.to_parent: Dict[int, int] = {}
        self.node_id_counter = itertools.count(0)
        self.depth = 1
        self.size = 1
        self.var_nodes = []

    def duplicate(self, _id: int) -> "Tree":
        ret = Tree(_id)
        # ret.nodes = copy.copy(self.nodes)
        ret.nodes = {}
        for key, val in self.nodes.items():
            if isinstance(val, Hole) or isinstance(val, Node):
                ret.nodes[key] = val.duplicate()
            else:
                ret.nodes[key] = val
        ret.to_children = self.to_children.copy()
        ret.to_parent = self.to_parent.copy()
        ret.node_id_counter = itertools.tee(self.node_id_counter)[1]
        ret.var_nodes = self.var_nodes.copy()
        ret.depth = self.depth
        ret.size = self.size
        return ret

    def __lt__(self, other):
        if self.size == other.size and self.depth == other.depth:
            return self.id < other.id
        if self.size == other.size:
            return self.depth < other.depth
        return self.size < other.size


class Synthesizer:
    """
    Interface for synthesizer with some shared functions.
    """

    def __init__(self, args, client, img_to_environment):
        self.max_synth_depth = args.max_synth_depth
        self.max_prog_depth = args.max_prog_depth
        self.max_faces = args.max_faces
        self.max_rounds = args.max_rounds
        self.client = client
        self.gt_prog_id = 0
        self.logs = []
        self.synthesis_overview = []
        self.img_to_environment = img_to_environment
        self.full_env = {}
        self.program_counter = itertools.count(0)
        self.synthesis_overview.append(
            (
                "Ground Truth Program",
                "Extracted Program",
                "Round",
                "# Objects",
                "FTA Construction Time",
                "# Enumerated Programs",
            )
        )
        for lib in img_to_environment.values():
            self.full_env = self.full_env | lib["environment"]

    def perform_synthesis(self, gt_prog=None, auto=False, example_imgs=[]):
        raise NotImplementedError

    def find_distinguishing_img(self, fta, abstract_fta, img_to_environment, action):
        raise NotImplementedError

    def get_indices(self, env, gt_prog):
        """
        Given the ground truth program, and the input image, automatically find out which are the labels by running the program on this input
        """
        ids = eval_extractor(gt_prog, env)
        return [env[obj_id]["ObjPosInImgLeftToRight"] for obj_id in ids]

    def get_differing_images(self, prog1, prog2) -> bool:
        """
        Returns the list of images on which 2 programs have different outputs
        """

        print("evaluating program equivalence")
        # print("prog1:", prog1)
        # print("prog2:", prog2)

        assert len(self.img_to_environment) > 0
        incorrect_img_ids = []

        for img_id, lib in self.img_to_environment.items():

            env = lib["environment"]
            ids1 = eval_extractor(prog1, env)
            ids2 = eval_extractor(prog2, env)

            # print("ids1:", ids1)
            # print("ids2:", ids2)

            if ids1 != ids2:
                # print("image id:", img_id)
                incorrect_img_ids.append(img_id)

        print("Programs differ on " + str(len(incorrect_img_ids)) + " images")
        print("Differing images: ", incorrect_img_ids)
        return incorrect_img_ids

    def synthesize_top_down(self, env, action, eval_cache):
        output = {key for (key, details) in env.items() if "ActionApplied" in details}
        card = len(output)

        output_dict = {}
        output_dict[str(output)] = output
        seen_progs = set()

        tree = Tree(next(self.program_counter))
        tree.nodes[0] = Hole(0, "extr", str(output), str(output))
        tree.var_nodes.append(0)
        worklist = []
        hq.heappush(worklist, tree)
        output_objs_str = get_output_objs(env, action)
        num_progs = 0

        while worklist:
            num_progs += 1
            cur_tree = hq.heappop(worklist)
            prog = construct_prog_from_tree(cur_tree)
            if not get_type(prog):
                continue
            # EQUIVALENCE REDUCTION
            should_prune = partial_eval(prog, env, output_dict, eval_cache, True)
            if should_prune:
                continue
            if not isinstance(prog, Hole):
                simplified_prog = simplify(prog.duplicate(), len(env), output_dict)
                if simplified_prog is None or str(simplified_prog) in seen_progs:
                    continue
                seen_progs.add(str(simplified_prog))
            if not cur_tree.var_nodes:
                extracted_objs = eval_extractor(
                    prog, env, output_dict=output_dict, eval_cache=eval_cache
                )
                extracted_objs_str = ",".join(sorted(extracted_objs))
                if extracted_objs_str == output_objs_str:
                    print("Num progs: ", num_progs)
                    print("Size:", cur_tree.size)
                    return prog, num_progs
                continue
            if num_progs % 1000 == 0:
                print(num_progs)
                print(prog)
                print(cur_tree.size)
                print()
            hole_num = cur_tree.var_nodes.pop(0)
            hole = cur_tree.nodes[hole_num]
            if hole.depth > self.max_synth_depth:
                print("Max depth reached")
                continue
            node_type = cur_tree.nodes[hole_num].node_type
            parent_node = (
                None if hole_num == 0 else cur_tree.nodes[cur_tree.to_parent[hole_num]]
            )
            if node_type == "extr":
                new_sub_extrs = get_extractors(
                    parent_node,
                    output_dict[hole.output_over],
                    output_dict[hole.output_under],
                    env,
                )
            elif node_type == "attr":
                new_sub_extrs = get_attributes(
                    output_dict[hole.output_over], output_dict[hole.output_under]
                )
            elif node_type == "age":
                new_sub_extrs = [(18, [], [], [], 0)]
            elif node_type == "index":
                new_sub_extrs = [
                    (index, [], [], [], 0)
                    for index in get_valid_indices(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            elif node_type == "word":
                new_sub_extrs = [
                    (word, [], [], [], 0)
                    for word in get_valid_words(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            elif node_type == "obj":
                new_sub_extrs = [
                    (obj, [], [], [], 0)
                    for obj in get_valid_objects(
                        env,
                        output_dict[hole.output_under],
                        output_dict[hole.output_over],
                    )
                ]
            for (
                sub_extr,
                children,
                child_outputs_over,
                child_outputs_under,
                size,
            ) in new_sub_extrs:
                if isinstance(sub_extr, Node):
                    sub_extr.output_over = str(hole.output_over)
                    sub_extr.output_under = str(hole.output_under)
                prog_output = get_prog_output(sub_extr, env, parent_node)
                # OUTPUT ESTIMATION-BASED PRUNING
                if prog_output and invalid_output(
                    output_dict[hole.output_over],
                    output_dict[hole.output_under],
                    prog_output,
                ):
                    continue
                new_tree = cur_tree.duplicate(next(self.program_counter))
                new_tree.nodes[hole_num] = sub_extr
                new_tree.size += size
                for child, child_output_over, child_output_under in zip(
                    children, child_outputs_over, child_outputs_under
                ):
                    over_str = str(child_output_over)
                    under_str = str(child_output_under)
                    if over_str not in output_dict:
                        output_dict[over_str] = child_output_over
                    if under_str not in output_dict:
                        output_dict[under_str] = child_output_under
                    new_hole = Hole(hole.depth + 1, child, over_str, under_str)
                    new_tree.depth = max(new_tree.depth, new_hole.depth)
                    new_node_num = len(new_tree.nodes)
                    new_tree.nodes[new_node_num] = new_hole
                    new_tree.var_nodes.append(new_node_num)
                    new_tree.to_parent[new_node_num] = hole_num
                    if hole_num in new_tree.to_children:
                        new_tree.to_children[hole_num].append(new_node_num)
                    else:
                        new_tree.to_children[hole_num] = [new_node_num]
                hq.heappush(worklist, new_tree)
        return None

    def get_environment(self, indices, img_dir, img_to_environment, action=Blur()):
        img_index = img_to_environment[img_dir]["img_index"]
        trace = [(img_index, i) for i in indices]
        env = img_to_environment[img_dir]["environment"]
        ex = IOExample(
            {action: trace},
            [img_dir],
            self.client,
            "",
            "",
            self.max_faces,
            img_to_environment=img_to_environment,
        )
        return env

    def perform_synthesis(
        self,
        gt_prog=None,
        example_imgs=[],
        annotated_imgs=[],
        testing=True,
        interactive=False,
        time_limit=300,
    ):
        print("Starting synthesis!")
        print()
        if gt_prog:
            print("Ground truth program: ", gt_prog)
        img_to_environment = self.img_to_environment.copy()
        img_dirs = []
        # assuming one action for now
        action = Blur()
        fta = None
        rounds = 1
        total_synthesis_time = 0
        annotated_env = {}
        objs = set()
        img_options = list(img_to_environment.keys())
        while rounds <= self.max_rounds:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(time_limit)
            try:
                start_time = time.perf_counter()
                if testing:
                    # Using manually chosen example images
                    if example_imgs:
                        for img_dir in example_imgs:
                            img_dirs.append(img_dir)
                            env = img_to_environment[img_dir]["environment"]
                            indices = self.get_indices(env, gt_prog)
                            annotated_env = (
                                self.get_environment(
                                    indices, img_dir, img_to_environment
                                )
                                | annotated_env
                            )
                    # Interactive testing
                    elif interactive:
                        while True:
                            filepath = filedialog.askopenfilename(
                                title="Select an Image",
                                filetypes=(("images", "*.jpg"), ("all files", "*.*")),
                            )
                            img_dir = filepath.split("ImageEye/")[1]
                            env = img_to_environment[img_dir]["environment"]
                            action_to_objects = annotate_image(img_dir, env)
                            # TODO: (maybe) Support multiple actions?
                            # TODO: (definitely) support multiple images
                            (action, indices) = list(action_to_objects.items())[0]
                            annotated_env = (
                                self.get_environment(
                                    indices, img_dir, img_to_environment, action
                                )
                                | annotated_env
                            )
                            should_continue = input("Add another image? (y/n)")
                            if should_continue == "n":
                                break
                    # Automatically chosen examples using heuristic
                    else:
                        print("Starting round ", rounds)
                        print()
                        img_dir, _ = min(
                            [
                                (img_dir, img_to_environment[img_dir]["environment"])
                                for img_dir in img_options
                            ],
                            key=lambda tup: (len(tup[1]), str(tup[0])),
                        )
                        print("New image: ", img_dir)
                        env = img_to_environment[img_dir]["environment"]
                        indices = self.get_indices(env, gt_prog)
                        if rounds == 1 and not indices:
                            img_options.remove(img_dir)
                            continue
                        img_dirs.append(img_dir)
                        annotated_env = (
                            self.get_environment(indices, img_dir, img_to_environment)
                            | annotated_env
                        )
                else:
                    if annotated_imgs:
                        for img_dir, indices in annotated_imgs:
                            annotated_env = (
                                self.get_environment(
                                    indices, img_dir, img_to_environment
                                )
                                | annotated_env
                            )
                num_attributes = get_num_attributes(annotated_env)
                construction_start_time = time.perf_counter()
                prog, num_progs = self.synthesize_top_down(annotated_env, action, {})
                print("Program: ", prog)
                construction_end_time = time.perf_counter()
                construction_time = construction_end_time - construction_start_time
                row = (
                    gt_prog,
                    prog,
                    rounds,
                    len(annotated_env),
                    construction_time,
                    num_progs,
                )
                self.synthesis_overview.append(row)
                if interactive:
                    print("Finished round ", rounds)
                    print("Synthesized program: ", prog)
                    for img_dir, env in img_to_environment.items():
                        img = cv2.imread(img_dir, 1)
                        edited_img = eval_apply_action(
                            ApplyAction(action, prog),
                            env["environment"],
                            [img],
                            self.client,
                        )[0]
                        img_name = img_dir.split("/")[-1]
                        cv2.imwrite("output/" + img_name, edited_img)
                    print("Images written to output directory")
                    response = input("Continue?")
                    if response == "n":
                        break
                    else:
                        continue
                # the list of images where synthesized prog and gt_prog have different outputs
                if testing:
                    img_options = self.get_differing_images(prog, gt_prog)
                else:
                    img_options = []
                # if list is empty, synthesized program is correct
                if not img_options:
                    print("Finished synthesis.")
                    print("Program: ", str(prog))
                    end_time = time.perf_counter()
                    cur_round_time = end_time - start_time
                    total_synthesis_time += cur_round_time
                    print("Number of rounds: ", str(rounds))
                    print("Total Synthesis Time: ", str(total_synthesis_time))
                    return (
                        prog,
                        cur_round_time,
                        rounds,
                        img_dirs,
                        len(annotated_env),
                        num_attributes,
                    )
                if example_imgs:
                    break
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                total_synthesis_time += cur_round_time
                rounds += 1
            except TimeOutException:
                end_time = time.perf_counter()
                cur_round_time = end_time - start_time
                print("TIMEOUT")
                return (
                    "TIMEOUT",
                    cur_round_time,
                    rounds,
                    img_dirs,
                    len(annotated_env),
                    num_attributes,
                )
        if interactive:
            print("Done!")
            return
        print("Synthesis failed.")
        print(rounds)
        return None, 0, rounds, img_dirs, len(annotated_env), num_attributes


if __name__ == "__main__":

    args = get_args()
    client = get_client()
    img_folder = "example_imgs/"
    img_to_environment = preprocess(img_folder, args.max_faces)
    synth = Synthesizer(args, client, img_to_environment)
    synth.perform_synthesis(
        gt_prog=None,
        example_imgs=[],
        interactive=True,
        testing=True,
        time_limit=args.time_limit,
    )
