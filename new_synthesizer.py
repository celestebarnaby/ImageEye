import itertools
from new_dsl import *
from new_interpreter import *


def get_relations():
    return [IsAbove, IsLeft, IsNextTo, IsInside]


def get_vals(img_to_env):
    vals = set()
    for env in img_to_env.values:
        for obj in env.values():
            if obj["Type"] == "Object":
                vals.add(obj["Name"])
            elif obj["Type"] == "Face":
                vals.add("face")
                vals.add("id" + str(obj["Index"]))
                if "Smile" in obj:
                    vals.add("smiling_face")
                if "EyesOpen" in obj:
                    vals.add("eyes_open_face")
    return vals


def fill_in_holes(tree, example_images, img_to_env):
    worklist = [tree]
    num_iters = 0
    while worklist:
        num_iters += 1
        cur_tree = worklist.pop(0)
        if not cur_tree.var_nodes:
            prog = construct_prog_from_tree(cur_tree)
            matching = True
            for img, result in example_images:
                env = img_to_env[img]
                if eval_prog(prog, env) != result:
                    matching = False
                    break
            if matching:
                return prog
        hole_num = cur_tree.var_nodes.pop(0)
        hole = cur_tree.nodes[hole_num]
        node_type = hole.node_type
        if node_type == "relation":
            new_sub_progs = get_relations()
        elif node_type == "var":
            new_sub_progs = get_vals(img_to_env)
        for sub_prog in new_sub_progs:
            new_tree = cur_tree.duplicate(num_iters)
            new_tree.nodes[hole_num] = sub_prog
            worklist.append(new_tree)
    return None
