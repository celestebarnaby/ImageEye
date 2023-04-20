from dsl import *
from typing import Any, List, Dict
from image_utils import *
import argparse
import os
import json
import csv
import time
import numpy as np
import random

DETAIL_KEYS = [
    "Eyeglasses",
    "Sunglasses",
    "Beard",
    "Mustache",
    "EyesOpen",
    "Smile",
    "MouthOpen",
    "Emotions",
    "AgeRange",
]


class TimeOutException(Exception):
    def __init__(self, message, errors=None):
        super(TimeOutException, self).__init__(message)
        self.errors = errors


class Hole:
    def __init__(self, depth, node_type, output_over=None, output_under=None, val=None):
        self.depth = depth
        self.node_type = node_type
        self.output_over = output_over
        self.output_under = output_under
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


def handler(signum, frame):
    raise TimeOutException("Timeout")


pos_to_types = {
    "GetLeft": {"Text"},
    "GetRight": {"Text"},
    "GetAbove": {"Text", "Face", "Object"},
    "GetBelow": {"Text", "Face", "Object"},
    "GetContains": {"Object"},
    "GetIsContained": {"Text", "Face", "Object"},
    "GetNext": {"Face", "Object"},
    "GetPrev": {"Face", "Object"},
}


def get_productions(env, states, depth):

    positions = [
        GetLeft(),
        GetRight(),
        GetAbove(),
        GetBelow(),
        GetContains(),
        GetIsContained(),
        GetNext(),
        GetPrev(),
    ]

    prods = []
    if depth == 0:
        prods += [
            (IsFace(), {"Face"}),
            (IsText(), {"Text"}),
            (IsPhoneNumber(), {"Text"}),
            (IsPrice(), {"Text"}),
            (IsSmiling(), {"Face"}),
            (MouthOpen(), {"Face"}),
            (EyesOpen(), {"Face"}),
            (BelowAge(18), {"Face"}),
            (AboveAge(18), {"Face"}),
        ]
        prods += [(GetFace(i), {"Face"}) for i in get_valid_indices(env)]
        prods += [(IsObject(obj), {"Object"})
                  for obj in get_valid_objects(env)]
        prods += [(MatchesWord(word), {"Text"})
                  for word in get_valid_words(env)]
    for pos in positions:
        prods.append((Map(None, pos), pos_to_types[str(pos)]))
    prods += [
        (Union(None, state), {"Face", "Text", "Object"}) for state in states.values()
    ]
    prods += [
        (Intersection(None, state), {"Face", "Text", "Object"})
        for state in states.values()
    ]
    prods += [(Complement(None), {"Face", "Text", "Object"})]

    return prods


def simplify(prog, env_size, output_dict):
    if isinstance(prog, Union) or isinstance(prog, Intersection):
        for sub_extr in prog.extractors:
            prog.extractors = [
                simplify(sub_extr, env_size, output_dict)
                for sub_extr in prog.extractors
            ]
            if None in prog.extractors:
                return None
    elif isinstance(prog, Complement) or isinstance(prog, Map):
        prog.extractor = simplify(prog.extractor, env_size, output_dict)
        if prog.extractor is None:
            return None
    pos_to_inverse = {
        "GetLeft": GetRight(),
        "GetRight": GetLeft(),
        "GetAbove": GetBelow(),
        "GetBelow": GetAbove(),
        "GetNext": GetPrev(),
        "GetPrev": GetNext(),
        "GetContains": GetIsContained(),
        "GetIsContained": GetContains(),
    }

    new_prog = None
    while True:
        changed = True
        if isinstance(prog, Union):
            if len(prog.extractors) == 1:
                new_prog = prog.extractors[0]
            else:
                new_sub_extrs = []
                for i, sub_extr in enumerate(prog.extractors):
                    val = (
                        output_dict[sub_extr.val] if sub_extr.val is not None else None
                    )
                    # Identity
                    if val is not None and len(val) == 0:
                        continue
                    if (
                        isinstance(sub_extr, Union)
                        or isinstance(sub_extr, Intersection)
                        and not sub_extr.extractors
                    ):
                        continue
                    # Domination
                    if val is not None and len(val) == env_size:
                        new_sub_extrs = [sub_extr]
                        break
                    should_keep = True
                    for j, other_sub_extr in enumerate(prog.extractors):
                        # Idempotency
                        if sub_extr == other_sub_extr and i < j:
                            should_keep = False
                            break
                        if (
                            val is not None
                            and other_sub_extr.val is not None
                            and val.issubset(output_dict[other_sub_extr.val])
                            and i != j
                        ):
                            should_keep = False
                            break
                        # Absorption
                        if (
                            isinstance(sub_extr, Intersection)
                            and other_sub_extr in sub_extr.extractors
                        ):
                            should_keep = False
                            break
                    if should_keep:
                        new_sub_extrs.append(sub_extr)
                new_sub_extrs.sort()
                if new_sub_extrs == prog.extractors:
                    changed = False
                if len(new_sub_extrs) < 2:
                    return None
                new_prog = Union(new_sub_extrs)

        elif isinstance(prog, Intersection):
            if len(prog.extractors) == 1:
                new_prog = prog.extractors[0]
            else:
                new_sub_extrs = []
                for i, sub_extr in enumerate(prog.extractors):
                    val = (
                        output_dict[sub_extr.val] if sub_extr.val is not None else None
                    )
                    should_keep = True
                    # Identity
                    if val is not None and len(val) == env_size:
                        continue
                    if (
                        isinstance(sub_extr, Union)
                        or isinstance(sub_extr, Intersection)
                        and not sub_extr.extractors
                    ):
                        continue
                    # Domination
                    if val is not None and len(val) == 0:
                        new_sub_extrs = [sub_extr]
                        break
                    for j, other_sub_extr in enumerate(prog.extractors):
                        # Idempotency
                        if sub_extr == other_sub_extr and i < j:
                            should_keep = False
                            break
                        if (
                            val is not None
                            and other_sub_extr.val is not None
                            and output_dict[other_sub_extr.val].issubset(val)
                            and i != j
                        ):
                            should_keep = False
                            break
                        # Absorption
                        if (
                            isinstance(sub_extr, Union)
                            and other_sub_extr in sub_extr.extractors
                        ):
                            should_keep = False
                            break
                    if should_keep:
                        new_sub_extrs.append(sub_extr)
                new_sub_extrs.sort()
                if new_sub_extrs == prog.extractors:
                    changed = False
                if len(new_sub_extrs) < 2:
                    return None
                new_prog = Intersection(new_sub_extrs)

        # Double negation
        elif isinstance(prog, Complement) and isinstance(prog.extractor, Complement):
            return None
            # new_prog = prog.extractor.extractor

        # Map inverse
        elif (
            isinstance(prog, Map)
            and isinstance(prog.extractor, Map)
            and pos_to_inverse[str(prog.position)] == prog.extractor.position
        ):
            new_prog = prog.extractor.extractor

        elif isinstance(prog, Complement) and isinstance(prog.extractor, Intersection):
            new_sub_extrs = [
                Complement(sub_extr) for sub_extr in prog.extractor.extractors
            ]
            new_prog = Union(new_sub_extrs)
        elif isinstance(prog, Complement) and isinstance(prog.extractor, Union):
            new_sub_extrs = [
                Complement(sub_extr) for sub_extr in prog.extractor.extractors
            ]
            new_prog = Intersection(new_sub_extrs)
        else:
            new_prog = prog
            changed = False

        if not changed:
            break
        prog = new_prog
    return prog


def get_output_objs(env, action):
    objs = set()
    # print("env:", env)
    for obj_id, details_map in env.items():
        if "ActionApplied" in details_map and details_map["ActionApplied"] == action:
            objs.add(obj_id)
    return ",".join(sorted(objs))


def compare_objs_with_output(env, objs, action):
    match = True
    for id_ in objs:
        if "ActionApplied" not in env[id_] or env[id_]["ActionApplied"] != action:
            match = False
    for id_, details_map in env.items():
        if (
            "ActionApplied" in details_map
            and details_map["ActionApplied"] == action
            and not id_ in objs
        ):
            match = False
    return match


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


def get_max_scoring_image(img_to_environment):
    return max(img_to_environment, key=lambda k: img_to_environment[k]["score"])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_synth_depth",
        type=int,
        default=5,
        help="max depth of FTA during construction",
    )
    parser.add_argument(
        "--max_prog_depth",
        type=int,
        default=20,
        help="max depth of synthesized program",
    )
    parser.add_argument(
        "--benchmark_set", type=str, default="wedding", help="set of benchmarks to use"
    )
    parser.add_argument(
        "--max_faces",
        type=int,
        default=100,
        help="max faces to detect in a single image",
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=180,
        help="time out limit for synthesis (seconds)",
    )
    parser.add_argument(
        "--synth_version", type=int, default=5, help="which synthesizer to use"
    )
    parser.add_argument(
        "--max_rounds", type=int, default=10, help="max number of synthesis rounds"
    )
    parser.add_argument(
        "--interactive",
        type=bool,
        default=False,
        help="set to True for interactive testing",
    )
    parser.add_argument(
        "--use_examples",
        type=bool,
        default=False,
        help="hand-picked examples versus heuristically chosen examples",
    )
    parser.add_argument(
        "--equiv_reduction",
        type=bool,
        default=True,
        help="set to False to turn off equivalence reduction"
    )
    parser.add_argument(
        "--partial_eval",
        type=bool,
        default=True,
        help="set to False to turn off partial evaluation"
    )
    parser.add_argument(
        "--goal_inference",
        type=bool,
        default=True,
        help="set to False to turn off partial evaluation"
    )
    parser.add_argument(
        "--use_active_learning",
        type=bool,
        default=True
    )
    parser.add_argument(
        "--get_dataset_info",
        type=bool,
        default=True,
        help="if True, outputs info about test dataset"
    )
    parser.add_argument(
        "--use_ground_truth",
        type=bool,
        default=True
    )
    args = parser.parse_args()
    return args


def get_type(prog):
    if not isinstance(prog, Node):
        return {"Face", "Text", "Object"}
    if isinstance(prog, Union):
        res = set()
        for sub_extr in prog.extractors:
            sub_extr_type = get_type(sub_extr)
            if not sub_extr_type:
                return sub_extr_type
            res = res.union(get_type(sub_extr))
        return res
    elif isinstance(prog, Intersection):
        res = {"Face", "Text", "Object"}
        for sub_extr in prog.extractors:
            res = res.intersection(get_type(sub_extr))
        return res
    elif isinstance(prog, Complement):
        return get_type(prog.extractor)
    elif (
        isinstance(prog, MatchesWord)
        or isinstance(prog, IsText)
        or isinstance(prog, IsPrice)
        or isinstance(prog, IsPhoneNumber)
    ):
        return {"Text"}
    elif (
        isinstance(prog, GetFace)
        or isinstance(prog, IsFace)
        or isinstance(prog, AboveAge)
        or isinstance(prog, BelowAge)
        or isinstance(prog, IsSmiling)
        or isinstance(prog, MouthOpen)
        or isinstance(prog, EyesOpen)
    ):
        return {"Face"}
    elif isinstance(prog, IsObject):
        return {"Object"}
    elif isinstance(prog, Map):
        map_type = get_type(prog.extractor).intersection(
            get_type(prog.position))
        if not map_type:
            return map_type
        return get_type(prog.restriction)
    elif isinstance(prog, Position):
        return pos_to_types[str(prog)]


def preprocess(img_folder, max_faces=10):
    """
    Given an img_folder, cache all the image's information to a dict, scored by the strategy
    """

    print("loading images and preprocessing...")

    # read the cache if it exists
    key = img_folder + " 2 " + str(max_faces)
    test_images = {}
    if os.path.exists("test_images.json"):
        with open("test_images.json", "r") as fp:
            test_images = json.load(fp)
            if key in test_images:
                return test_images[key]
    client = get_client()
    client.delete_collection(CollectionId="library2")
    client.create_collection(CollectionId="library2")
    img_to_environment = {}
    prev_env = {}
    img_index = 0

    start_time = time.perf_counter()
    # loop through all image files to cache information
    for filename in os.listdir(img_folder):
        # print("filename:", filename)
        img_dir = img_folder + filename
        env = get_environment(
            img_dir, client, img_index, DETAIL_KEYS, prev_env, max_faces
        )
        # print("environment:", env)
        score = len(env)
        # print("score:", score)
        img_to_environment[img_dir] = {
            "ground_truth": env,
            "model_env": noisify_env(env),
            "img_index": img_index,
            "score": score,
        }
        if not env:
            continue
        img_index += 1
        prev_env = prev_env | env
    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("preprocessing finished...")

    clean_environment(img_to_environment)
    print("Num images: ", len(os.listdir(img_folder)))
    print("Total time: ", total_time)
    test_images[key] = img_to_environment
    with open("test_images.json", "w") as fp:
        json.dump(test_images, fp)
    print(img_to_environment)

    return img_to_environment


def noisify_env(env):
    noisy_env = {}
    for obj_id, details in env.items():
        new_details = details.copy()
        noisy_env[obj_id] = new_details
        if details['Type'] != 'Face':
            continue
        for key in {'Smile', 'EyesOpen', 'MouthOpen'}:
            rand1 = random.random()
            if rand1 > .8:
                if key in new_details:
                    del new_details[key]
                    continue
                if key not in new_details:
                    new_details[key] = True
    return noisy_env


# Replace obj hashes with readable obj ids
def clean_environment(img_to_environment):
    new_id = "0"
    for lib in img_to_environment.values():
        new_ground_truth = {}
        new_model_env = {}
        gt = lib["ground_truth"]
        labels = lib["model_env"]
        for obj_hash, details in gt.items():
            new_ground_truth[new_id] = details
            new_model_env[new_id] = labels[obj_hash]
            new_id = str(int(new_id) + 1)
        lib["ground_truth"] = new_ground_truth
        lib["model_env"] = new_model_env


def write_logs(logs):
    total_time_per_task = {}
    for row in logs:
        task = row[:2]
        if task not in total_time_per_task:
            total_time_per_task[task] = 0
        total_time_per_task[task] += row[7]
    for task, total_time in total_time_per_task.items():
        row = (task[0] + "_TOTAL", task[1], "", "", "", "", "", total_time)
        logs.append(row)
    with open("data/logs.csv", "w") as f:
        fw = csv.writer(f)
        fw.writerow(
            (
                "Operation",
                "Task ID",
                "# Objects",
                "# States",
                "# Transitions",
                "Max CPU Usage",
                "Max Memory Usage",
                "Total Time",
            )
        )
        for row in logs:
            fw.writerow(row)


def write_synthesis_overview(logs):
    filename = "data/synthesis_overview.csv"
    with open("data/synthesis_overview.csv", "w") as f:
        fw = csv.writer(f)
        for row in logs:
            fw.writerow(row)


def get_positions() -> List[Position]:
    return [
        GetLeft(),
        GetRight(),
        GetAbove(),
        GetBelow(),
        GetContains(),
        GetIsContained(),
        GetNext(),
        GetPrev(),
    ]


def get_valid_indices(env, output_under, output_over):
    req_indices = set(
        [env[obj_id]["Index"]
            for obj_id in output_under if "Index" in env[obj_id]]
    )
    if len(req_indices) == 1:
        return req_indices
    if len(req_indices) > 1:
        return []
    return sorted(
        list(
            set(
                [
                    env[obj_id]["Index"]
                    for obj_id in output_over
                    if "Index" in env[obj_id]
                ]
            )
        )
    )


def get_valid_words(env, output_under, output_over):
    req_words = set(
        [
            env[obj_id]["Text"].lower()
            for obj_id in output_under
            if "Text" in env[obj_id]
        ]
    )
    if len(req_words) == 1:
        return req_words
    if len(req_words) > 1:
        return []
    return sorted(
        list(
            set(
                [
                    env[obj_id]["Text"].lower()
                    for obj_id in output_over
                    if "Text" in env[obj_id]
                ]
            )
        )
    )


def get_valid_objects(env, output_under, output_over):
    req_objects = set(
        [env[obj_id]["Name"]
            for obj_id in output_under if "Name" in env[obj_id]]
    )
    if len(req_objects) == 1:
        return req_objects
    if len(req_objects) > 1:
        return []
    return sorted(
        list(
            set(
                [env[obj_id]["Name"]
                    for obj_id in output_over if "Name" in env[obj_id]]
            )
        )
    )


def invalid_output(output_over, output_under, prog_output):
    return not (
        output_under.issubset(
            prog_output) and prog_output.issubset(output_over)
    )


def get_num_attributes(env):
    all_preds = set()
    text_to_id = {}
    for obj in env.values():
        preds = set()
        for key, val in obj.items():
            if key == "Type" and val != "Object":
                preds.add(key + val)
            elif key == "Name":
                preds.add(key + val.replace(" ", ""))
            elif key == "Text":
                if val in text_to_id:
                    text_id = text_to_id[val]
                elif not text_to_id:
                    text_id = 0
                    text_to_id[val] = text_id
                else:
                    text_id = max(text_to_id.values()) + 1
                    text_to_id[val] = text_id
                preds.add(key + str(text_id))
            elif key == "AgeRange":
                if val["High"] < 18:
                    preds.add("BelowAge18")
            elif key == "Index" and obj["Type"] == "Face":
                preds.add(key + str(val))
            elif key in DETAIL_KEYS:
                preds.add(key)
        all_preds.update(preds)
    return len(all_preds)
