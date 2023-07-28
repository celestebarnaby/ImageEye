from new_dsl import *
from new_interpreter import *


def get_relations():
    return [
        Is(None, None),
        IsAbove(None, None),
        IsLeft(None, None),
        IsNextTo(None, None),
        IsInside(None, None),
    ]


def get_objects(img_to_env, examples=None):
    vals = set()
    for img, env in img_to_env.items():
        if examples is not None and img not in examples:
            continue
        env = env["environment"]
        for obj in env.values():
            if obj["Type"] == "Object":
                vals.add(obj["Name"].lower())
            elif obj["Type"] == "Face":
                vals.add("face")
                vals.add("id" + str(obj["Index"]))
                if "Smile" in obj:
                    vals.add("smiling_face")
                if "EyesOpen" in obj:
                    vals.add("eyes_open_face")
    return vals


def construct_prog_from_tree(tree, node_num=0, should_copy=False):
    if should_copy:
        prog = copy.copy(tree.nodes[node_num])
    else:
        prog = tree.nodes[node_num]
    if not isinstance(prog, Formula):
        return prog
    prog_dict = vars(prog)
    if node_num in tree.to_children:
        child_nums = tree.to_children[node_num]
    else:
        child_nums = []
    child_types = [item for item in list(prog_dict) if item != "var"]
    # if child_types and child_types[0] == "extractors":
    #     for child_num in child_nums:
    #         prog_dict["extractors"].pop(0)
    #         child_prog = construct_prog_from_tree(tree, child_num)
    #         prog_dict["extractors"].append(child_prog)
    #     return prog
    # assert len(child_nums) == len(child_types)
    for child_type, child_num in zip(child_types, child_nums):
        child_prog = construct_prog_from_tree(tree, child_num)
        prog_dict[child_type] = child_prog
    return prog


def fill_in_holes(tree, example_images, img_to_env, objects):
    worklist = [tree]
    num_iters = 0
    if not example_images:
        return None, None
    start_time = time.perf_counter()
    while worklist:
        cur_time = time.perf_counter()
        if cur_time - start_time > 15:
            raise TimeoutError
        num_iters += 1
        cur_tree = worklist.pop(0)
        if not cur_tree.var_nodes:
            prog = construct_prog_from_tree(cur_tree)
            matching = True
            # if not example_images:
            #     return prog
            for img, result in example_images:
                env = img_to_env[img]["environment"]
                if eval_prog(prog, env) != result:
                    matching = False
                    break
            if matching:
                return prog, cur_tree.holes_to_vals
            continue
        hole_num = cur_tree.var_nodes.pop(0)
        hole = cur_tree.nodes[hole_num]
        node_type = hole.node_type
        if node_type == "relation":
            new_sub_progs = get_relations()
        elif node_type == "var":
            new_sub_progs = objects
        for sub_prog in new_sub_progs:
            new_tree = cur_tree.duplicate()
            if node_type == "var":
                new_tree.holes_to_vals[hole.val] = sub_prog
            new_tree.nodes[hole_num] = sub_prog
            worklist.append(new_tree)
    return None, None
