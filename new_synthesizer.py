import itertools
from new_dsl import *
from new_interpreter import *


class Hole:
    def __init__(self, node_type, val=None):
        self.node_type = node_type
        self.val = None

    def __str__(self):
        return type(self).__name__

    def duplicate(self):
        return Hole(
            self.depth, self.node_type, self.output_over, self.output_under, self.val
        )

    def __lt__(self, other):
        if not isinstance(other, Hole):
            return False
        return str(self) < str(other)


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


def construct_prog_from_tree(tree, node_num=0, should_copy=False):
    if should_copy:
        prog = copy.copy(tree.nodes[node_num])
    else:
        prog = tree.nodes[node_num]
    if not isinstance(prog, Node):
        return prog
    prog_dict = vars(prog)
    if node_num in tree.to_children:
        child_nums = tree.to_children[node_num]
    else:
        child_nums = []
    child_types = [
        item
        for item in list(prog_dict)
        if item not in {"position", "val", "age", "output_over", "output_under"}
    ]
    if child_types and child_types[0] == "extractors":
        for child_num in child_nums:
            prog_dict["extractors"].pop(0)
            child_prog = construct_prog_from_tree(tree, child_num)
            prog_dict["extractors"].append(child_prog)
        return prog
    assert len(child_nums) == len(child_types)
    for child_type, child_num in zip(child_types, child_nums):
        child_prog = construct_prog_from_tree(tree, child_num)
        prog_dict[child_type] = child_prog
    return prog


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
        node_type = cur_tree.nodes[hole_num].node_type
        if node_type == "relation":
            new_sub_progs = get_relations()
        elif node_type == "var":
            new_sub_progs = get_vals(img_to_env)
        for sub_prog in new_sub_progs:
            new_tree = cur_tree.duplicate(num_iters)
            new_tree.nodes[hole_num] = sub_prog
            worklist.append(new_tree)
    return None
