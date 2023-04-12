import cv2
import csv
import numpy as np
import random
from benchmarks import benchmarks
from dsl import *
from image_utils import *
from utils import *
from typing import Any, List, Dict, Set, Tuple

map_outputs = {}


def partial_eval_map(map_extr, env, output_dict, eval_cache):
    if partial_eval(map_extr.extractor, env, output_dict, eval_cache):
        return True
    elif partial_eval(map_extr.restriction, env, output_dict, eval_cache):
        return True
    val = set()
    if map_extr.extractor.val is None or map_extr.restriction.val is None:
        return False
    extr_val = output_dict[map_extr.extractor.val]
    rest_val = output_dict[map_extr.restriction.val]
    if isinstance(map_extr.position, GetPrev):
        # The idea: for each target obj we extract, we need to identify
        # the obj who right boundary is as close to the target right boundary
        # as possible, without being greater.
        for target_obj_id in extr_val:
            pos = env[target_obj_id]["ObjPosInImgLeftToRight"]
            cur_obj_id = None
            cur_pos = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if details["ObjPosInImgLeftToRight"] >= pos:
                    continue
                if obj_id not in rest_val:
                    continue
                if cur_pos is None or details["ObjPosInImgLeftToRight"] > cur_pos:
                    cur_obj_id = obj_id
                    cur_pos = details["ObjPosInImgLeftToRight"]
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetNext):
        for target_obj_id in extr_val:
            pos = env[target_obj_id]["ObjPosInImgLeftToRight"]
            cur_obj_id = None
            cur_pos = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if details["ObjPosInImgLeftToRight"] <= pos:
                    continue
                if obj_id not in rest_val:
                    continue
                if cur_pos is None or details["ObjPosInImgLeftToRight"] < cur_pos:
                    cur_obj_id = obj_id
                    cur_pos = details["ObjPosInImgLeftToRight"]
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetBelow):
        for target_obj_id in extr_val:
            target_left, target_top, target_right, _ = env[target_obj_id]["Loc"]
            cur_obj_id = None
            cur_top = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                left, top, right, bottom = details["Loc"]
                if top < target_top:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_top is None or top < cur_top:
                    cur_top = top
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetAbove):
        for target_obj_id in extr_val:
            target_left, target_top, target_right, target_bottom = env[target_obj_id][
                "Loc"
            ]
            cur_obj_id = None
            cur_bottom = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                left, top, right, bottom = details["Loc"]
                if bottom > target_bottom:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_bottom is None or bottom > cur_bottom:
                    cur_bottom = bottom
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetLeft):
        for target_obj_id in extr_val:
            target_left, target_top, target_right, target_bottom = env[target_obj_id][
                "Loc"
            ]
            cur_obj_id = None
            cur_left = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                left, top, right, bottom = details["Loc"]
                if left > target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left > cur_left:
                    cur_left = left
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetRight):
        for target_obj_id in extr_val:
            target_left, target_top, target_right, target_bottom = env[target_obj_id][
                "Loc"
            ]
            cur_obj_id = None
            cur_left = None
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                left, top, right, bottom = details["Loc"]
                if left < target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left < cur_left:
                    cur_left = left
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                val.add(cur_obj_id)
    elif isinstance(map_extr.position, GetContains):
        for target_obj_id in extr_val:
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                if is_contained(details["Loc"], env[target_obj_id]["Loc"]):
                    val.add(obj_id)
    elif isinstance(map_extr.position, GetIsContained):
        for target_obj_id in extr_val:
            for obj_id, details in env.items():
                if details["ImgIndex"] != env[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest_val:
                    continue
                if is_contained(env[target_obj_id]["Loc"], details["Loc"]):
                    val.add(obj_id)
    if len(val) == 0:
        return True
    map_extr.val = str(val)
    if str(val) not in output_dict:
        output_dict[str(val)] = val
    eval_cache[str(map_extr)] = val
    return False


def eval_map(
    map_extr: Map,
    details: Dict[str, Dict[str, Any]],
    rec: bool = True,
    output_dict={},
    eval_cache={},
) -> Set[str]:
    if rec:
        objs = eval_extractor(
            map_extr.extractor, details, output_dict=output_dict, eval_cache=eval_cache
        )
        rest = eval_extractor(
            map_extr.restriction,
            details,
            output_dict=output_dict,
            eval_cache=eval_cache,
        )
    else:
        objs = map_extr.extractor
        rest = map_extr.restriction
    mapped_objs = set()
    if isinstance(map_extr.position, GetPrev):
        # The idea: for each target obj we extract, we need to identify
        # the obj who right boundary is as close to the target right boundary
        # as possible, without being greater.
        for target_obj_id in objs:
            pos = details[target_obj_id]["ObjPosInImgLeftToRight"]
            cur_obj_id = None
            cur_pos = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if details_map["ObjPosInImgLeftToRight"] >= pos:
                    continue
                if obj_id not in rest:
                    continue
                if cur_pos is None or details_map["ObjPosInImgLeftToRight"] > cur_pos:
                    cur_obj_id = obj_id
                    cur_pos = details_map["ObjPosInImgLeftToRight"]
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetNext):
        for target_obj_id in objs:
            pos = details[target_obj_id]["ObjPosInImgLeftToRight"]
            cur_obj_id = None
            cur_pos = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if details_map["ObjPosInImgLeftToRight"] <= pos:
                    continue
                if obj_id not in rest:
                    continue
                if cur_pos is None or details_map["ObjPosInImgLeftToRight"] < cur_pos:
                    cur_obj_id = obj_id
                    cur_pos = details_map["ObjPosInImgLeftToRight"]
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetBelow):
        for target_obj_id in objs:
            target_left, target_top, target_right, _ = details[target_obj_id]["Loc"]
            cur_obj_id = None
            cur_top = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                left, top, right, bottom = details_map["Loc"]
                if top < target_top:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_top is None or top < cur_top:
                    cur_top = top
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetAbove):
        for target_obj_id in objs:
            target_left, target_top, target_right, target_bottom = details[
                target_obj_id
            ]["Loc"]
            cur_obj_id = None
            cur_bottom = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                left, top, right, bottom = details_map["Loc"]
                if bottom > target_bottom:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_bottom is None or bottom > cur_bottom:
                    cur_bottom = bottom
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetLeft):
        for target_obj_id in objs:
            target_left, target_top, target_right, target_bottom = details[
                target_obj_id
            ]["Loc"]
            cur_obj_id = None
            cur_left = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                left, top, right, bottom = details_map["Loc"]
                if left > target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left > cur_left:
                    cur_left = left
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetRight):
        for target_obj_id in objs:
            target_left, target_top, target_right, target_bottom = details[
                target_obj_id
            ]["Loc"]
            cur_obj_id = None
            cur_left = None
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                left, top, right, bottom = details_map["Loc"]
                if left < target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left < cur_left:
                    cur_left = left
                    cur_obj_id = obj_id
            if cur_obj_id is not None:
                mapped_objs.add(cur_obj_id)
    elif isinstance(map_extr.position, GetContains):
        for target_obj_id in objs:
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                if is_contained(details_map["Loc"], details[target_obj_id]["Loc"]):
                    mapped_objs.add(obj_id)
    elif isinstance(map_extr.position, GetIsContained):
        for target_obj_id in objs:
            for obj_id, details_map in details.items():
                if details_map["ImgIndex"] != details[target_obj_id]["ImgIndex"]:
                    continue
                if obj_id == target_obj_id:
                    continue
                if obj_id not in rest:
                    continue
                if is_contained(details[target_obj_id]["Loc"], details_map["Loc"]):
                    mapped_objs.add(obj_id)
    if rec:
        return mapped_objs
    else:
        return mapped_objs


def partial_eval(extractor, env, output_dict, eval_cache, top_level=False):
    if not isinstance(extractor, Extractor):
        return False

    if extractor.val is not None:
        return False

    if str(extractor) in eval_cache:
        val = eval_cache[str(extractor)]
        extractor.val = str(val)
        if len(val) == 0:
            return True
        return False

    faces = {obj for obj in env.keys(
    ) if env[obj]["Type"] == "Face" or "AlsoFace" in env[obj]}
    text_objects = {obj for obj in env.keys() if env[obj]["Type"] == "Text"}
    objects = {obj for obj in env.keys() if env[obj]["Type"] == "Object"}

    val = None
    if isinstance(extractor, IsFace):
        val = faces
    elif isinstance(extractor, IsText):
        val = text_objects
    elif isinstance(extractor, GetFace):
        val = set()
        if not faces:
            val = set()
        elif not isinstance(extractor.index, int):
            return False
        for (obj_id, details) in env.items():
            if details["Type"] != "Face" and not "AlsoFace" in details:
                continue
            if details["Index"] == extractor.index:
                val.add(obj_id)
    elif isinstance(extractor, IsObject):
        val = set()
        if not objects:
            val = set()
        elif not isinstance(extractor.obj, str):
            return False
        for (obj_id, details) in env.items():
            if details["Type"] != "Object":
                continue
            if details["Name"] == extractor.obj:
                val.add(obj_id)
    elif isinstance(extractor, MatchesWord):
        val = set()
        if not text_objects:
            val = set()
        elif not isinstance(extractor.word, str):
            return False
        for (obj_id, details) in env.items():
            if details["Type"] != "Text":
                continue
            if details["Text"].lower() == extractor.word.lower():
                val.add(obj_id)
    elif isinstance(extractor, BelowAge):
        val = set()
        if not faces:
            val = set()
        elif not isinstance(extractor.age, int):
            return False
        for (obj_id, details) in env.items():
            if details["Type"] != "Face":
                continue
            if extractor.age > details["AgeRange"]["Low"]:
                val.add(obj_id)
    elif isinstance(extractor, AboveAge):
        val = set()
        if not faces:
            val = set()
        elif not isinstance(extractor.age, int):
            return False
        for (obj_id, details) in env.items():
            if details["Type"] != "Face":
                continue
            if extractor.age < details["AgeRange"]["High"]:
                val.add(obj_id)
    elif isinstance(extractor, Union):
        should_prune = False
        for sub_extr in extractor.extractors:
            should_prune = (
                partial_eval(sub_extr, env, output_dict,
                             eval_cache) or should_prune
            )
        vals = []
        none_vals = []
        val_total = set()
        for i, sub_extr in enumerate(extractor.extractors):
            if sub_extr.val is None:
                none_vals.append(i)
            else:
                vals.append(output_dict[sub_extr.val])
                val_total.update(output_dict[sub_extr.val])
        if len(none_vals) == 1 and extractor.output_over == extractor.output_under:
            sub_extr = extractor.extractors[none_vals[0]]
            output_under = output_dict[sub_extr.output_under]
            output_over = output_dict[sub_extr.output_over]
            new_output_under = output_over - val_total
            update_output_approx(
                sub_extr, new_output_under, output_over, env, output_dict
            )
        if vals and not none_vals:
            val = set.union(*vals)
        elif set(env.keys()) in vals:
            val = set(env.keys())
        if should_prune:
            return True
    elif isinstance(extractor, Intersection):
        should_prune = False
        for sub_extr in extractor.extractors:
            should_prune = (
                partial_eval(sub_extr, env, output_dict,
                             eval_cache) or should_prune
            )
        vals = []
        none_vals = []
        val_total = set()
        for i, sub_extr in enumerate(extractor.extractors):
            if sub_extr.val is None:
                none_vals.append(i)
            else:
                vals.append(output_dict[sub_extr.val])
                val_total = val_total.intersection(output_dict[sub_extr.val])
        if len(none_vals) == 1 and extractor.output_over == extractor.output_under:
            sub_extr = extractor.extractors[none_vals[0]]
            output_under = output_dict[sub_extr.output_under]
            output_over = output_dict[sub_extr.output_over]
            new_output_over = set(env.keys()) - (val_total - output_under)
            update_output_approx(
                sub_extr, output_under, new_output_over, env, output_dict
            )
        if vals and not none_vals:
            val = set.intersection(*vals)
        elif set() in vals:
            val = set()
        if should_prune:
            return True
    elif isinstance(extractor, Complement):
        if partial_eval(extractor.extractor, env, output_dict, eval_cache):
            return True
        if extractor.extractor.val is not None:
            val = set(env.keys()) - output_dict[extractor.extractor.val]
    elif (
        isinstance(extractor, IsPhoneNumber)
        or isinstance(extractor, IsPrice)
        or isinstance(extractor, IsSmiling)
        or isinstance(extractor, EyesOpen)
        or isinstance(extractor, MouthOpen)
    ):
        val = {obj for obj in env if str(extractor) in env[obj]}
    elif isinstance(extractor, Map):
        return partial_eval_map(extractor, env, output_dict, eval_cache)
    if val is not None:
        extractor.val = str(val)
        eval_cache[str(extractor)] = val
        if str(val) not in output_dict:
            output_dict[str(val)] = val
        if len(val) == 0:
            return True
    return False


def update_output_approx(prog, output_under, output_over, env, output_dict):
    if (
        isinstance(prog, str)
        or isinstance(prog, int)
        or output_under == prog.output_under
        and output_over == prog.output_over
    ):
        return
    over_str = str(output_over)
    under_str = str(output_under)
    if over_str not in output_dict:
        output_dict[over_str] = output_over
    if under_str not in output_dict:
        output_dict[under_str] = output_under
    prog.output_under = under_str
    prog.output_over = over_str
    if isinstance(prog, Union):
        for sub_extr in prog.extractors:
            update_output_approx(
                sub_extr, set(), output_over, env, output_dict)
    elif isinstance(prog, Intersection):
        for sub_extr in prog.extractors:
            update_output_approx(
                sub_extr, output_under, set(env.keys()), env, output_dict
            )
    elif isinstance(prog, Complement):
        update_output_approx(
            prog.extractor,
            set(env.keys()) - output_over,
            set(env.keys() - output_under),
            env,
            output_dict,
        )
    elif isinstance(prog, Map):
        update_output_approx(prog.extractor, set(),
                             set(env.keys()), env, output_dict)
        update_output_approx(
            prog.restriction, output_under, set(env.keys()), env, output_dict
        )
    elif isinstance(prog, MatchesWord):
        update_output_approx(prog.word, output_under,
                             output_over, env, output_dict)
    elif isinstance(prog, GetFace):
        update_output_approx(prog.index, output_under,
                             output_over, env, output_dict)
    elif isinstance(prog, IsObject):
        update_output_approx(prog.obj, output_under,
                             output_over, env, output_dict)


def eval_extractor(
    extractor: Extractor,
    details: Dict[str, Dict[str, Any]],
    rec: bool = True,
    output_dict={},
    eval_cache=None,
):  # -> Set[dict[str, str]]:
    if output_dict and extractor.val is not None:
        return output_dict[extractor.val]
    if eval_cache and str(extractor) in eval_cache:
        return eval_cache[str(extractor)]
    if isinstance(extractor, Map):
        res = eval_map(extractor, details, rec, output_dict, eval_cache)
    elif isinstance(extractor, IsFace):
        # list of all face ids in target image
        res = {obj for obj in details.keys() if details[obj]["Type"] == "Face" or (
            "AlsoFace" in details[obj])}
    elif isinstance(extractor, IsText):
        res = {obj for obj in details.keys() if details[obj]["Type"] == "Text"}
    elif isinstance(extractor, GetFace):
        objs = set()
        for (obj_id, obj_details) in details.items():
            if obj_details["Type"] != "Face" and not "AlsoFace" in obj_details:
                continue
            if obj_details["Index"] == extractor.index:
                objs.add(obj_id)
        res = objs
    elif isinstance(extractor, IsObject):
        objs = set()
        for (obj_id, obj_details) in details.items():
            if obj_details["Type"] != "Object":
                continue
            if obj_details["Name"] == extractor.obj:
                objs.add(obj_id)
        res = objs
    elif isinstance(extractor, MatchesWord):
        objs = set()
        for (obj_id, obj_details) in details.items():
            if obj_details["Type"] != "Text":
                continue
            if obj_details["Text"].lower() == extractor.word.lower():
                objs.add(obj_id)
        res = objs
    elif isinstance(extractor, BelowAge):
        objs = set()
        for (obj_id, obj_details) in details.items():
            if obj_details["Type"] != "Face":
                continue
            if extractor.age > obj_details["AgeRange"]["Low"]:
                objs.add(obj_id)
        res = objs
    elif isinstance(extractor, AboveAge):
        objs = set()
        for (obj_id, obj_details) in details.items():
            if obj_details["Type"] != "Face":
                continue
            if extractor.age < obj_details["AgeRange"]["High"]:
                objs.add(obj_id)
        res = objs
    elif isinstance(extractor, Union):
        if rec:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.union(
                    eval_extractor(sub_extr, details, rec,
                                   output_dict, eval_cache)
                )
            res = res
        else:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.union(sub_extr.objs)
            res = res
    elif isinstance(extractor, Intersection):
        if rec:
            res = set(details.keys())
            for sub_extr in extractor.extractors:
                res = res.intersection(
                    eval_extractor(sub_extr, details, rec,
                                   output_dict, eval_cache)
                )
        else:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.intersection(sub_extr.objs)
    elif isinstance(extractor, Complement):
        # All objs in target image except those extracted
        if rec:
            extracted_objs = eval_extractor(
                extractor.extractor, details, rec, output_dict, eval_cache
            )
            res = details.keys() - extracted_objs
        else:
            res = details.keys() - set(extractor.extractor.objs)
    elif (
        isinstance(extractor, IsPhoneNumber)
        or isinstance(extractor, IsPrice)
        or isinstance(extractor, IsSmiling)
        or isinstance(extractor, EyesOpen)
        or isinstance(extractor, MouthOpen)
    ):
        res = {obj for obj in details if str(extractor) in details[obj]}
    else:
        print(extractor)
        raise Exception
    if eval_cache:
        eval_cache[str(extractor)] = res
    return res


def eval_crop(extracted_objs, details_map, imgs):
    img = imgs[0]
    cur_coords = None
    for obj_id, details in details_map.items():
        if obj_id not in extracted_objs:
            continue
        if cur_coords is None:
            cur_coords = details["Loc"]
        else:
            cur_coords = (
                min(cur_coords[0], details["Loc"][0]),
                min(cur_coords[1], details["Loc"][1]),
                max(cur_coords[2], details["Loc"][2]),
                max(cur_coords[3], details["Loc"][3]),
            )
    left, top, right, bottom = cur_coords
    img = img[top:bottom, left:right]
    return [img]


def eval_apply_action(
    statement: Statement,
    details: Dict[str, Dict[str, Any]],
    imgs,
    extracted_objs=None,
):
    # list of all obj ids we want to apply action to
    if not extracted_objs:
        extracted_objs = eval_extractor(statement.extractor, details)
    action = statement.action
    if isinstance(action, Crop):
        return eval_crop(extracted_objs, details, imgs)
    for obj_id, details in details.items():
        img = imgs[0]
        if obj_id not in extracted_objs:
            continue
        apply_action_to_object(action, img, details)
    return imgs


def eval_program(prog: Program, imgs, details: Dict[str, Dict[str, Any]]):
    for statement in prog.statements:
        imgs = eval_apply_action(statement, details, imgs)
    else:
        for img in imgs:
            # Display image
            cv2.imshow("image", img)
            # Wait for a key to be pressed to exit
            cv2.waitKey(0)
            # Close the window
            cv2.destroyAllWindows()


def test_interpreter(args):
    print("hi")
    # TODO


if __name__ == "__main__":
    args = get_args()
    test_interpreter(args)
