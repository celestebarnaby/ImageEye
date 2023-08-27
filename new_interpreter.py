from new_dsl import *
from utils import *
from image_utils import *


def checkMatchingObj(var, obj):
    return (
        ((var == "face" or var == "person") and obj["Type"] == "Face")
        or (var == "smilingFace" and "Smile" in obj)
        or (var == "eyesOpenFace" and "EyesOpen" in obj)
        or (
            var.startswith("id")
            and var[2:].isdigit()
            and "Index" in obj
            and obj["Index"] == int(var[2:])
        )
        or (obj["Type"] == "Object" and obj["Name"].lower() == var.lower())
        or (
            obj["Type"] == "Object"
            and obj["Name"].lower() in name_to_parent
            and name_to_parent[obj["Name"].lower()] == var.lower()
        )
        or (("Tag" in obj and obj["Tag"].lower() == var.lower()))
    )


def checkIsAbove(obj1, obj2):
    left1, top1, right1, bottom1 = obj1["Loc"]
    left2, top2, right2, bottom2 = obj2["Loc"]
    center_y_1 = (top1 + bottom1) / 2
    center_y_2 = (top2 + bottom2) / 2
    if right1 < left2 or left1 > right2:
        return False
    return center_y_1 < center_y_2


def checkIsLeft(obj1, obj2):
    left1, top1, right1, bottom1 = obj1["Loc"]
    left2, top2, right2, bottom2 = obj2["Loc"]
    center_x_1 = (left1 + right1) / 2
    center_x_2 = (left2 + right2) / 2
    if bottom1 < top2 or top1 > bottom2:
        return False
    return center_x_1 < center_x_2


def eval_prog(prog, env, vars_to_vals={}):
    if isinstance(prog, Exists):
        for obj in env.values():
            vars_to_vals[prog.var] = obj
            if eval_prog(prog.subformula, env, vars_to_vals):
                return True
        return False
    if isinstance(prog, ForAll):
        for obj in env.values():
            vars_to_vals[prog.var] = obj
            if not eval_prog(prog.subformula, env, vars_to_vals):
                return False
        return True
    if isinstance(prog, And):
        return eval_prog(prog.subformula1, env, vars_to_vals) and eval_prog(
            prog.subformula2, env, vars_to_vals
        )
    if isinstance(prog, Not):
        return not eval_prog(prog.subformula, env, vars_to_vals)
    if isinstance(prog, Is):
        if prog.var1 not in vars_to_vals:
            return False
        val = vars_to_vals[prog.var1]
        if prog.var2 == "face" or prog.var2 == "person":
            return (
                val["Type"] == "Face"
                or val["Type"] == "Object"
                and val["Name"].lower() == "person"
            )
        if prog.var2 == "smilingFace":
            return "Smile" in val
        if prog.var2 == "eyesOpenFace":
            return "EyesOpen" in val
        if prog.var2.startswith("id") and prog.var2[2:].isdigit():
            return "Index" in val and val["Index"] == int(prog.var2[2:])
        if prog.var2.lower() in name_to_parent:
            val["Type"] == "Object" and (
                val["Name"].lower() == prog.var2.lower()
                or val["Name"].lower() == name_to_parent[prog.var2.lower()]
            )
        return (
            val["Type"] == "Object" and val["Name"].lower() == prog.var2.lower()
        ) or ("Tag" in val and val["Tag"].lower() == prog.var2.lower())
    if isinstance(prog, IfThen):
        if_eval = eval_prog(prog.subformula1, env, vars_to_vals)
        if if_eval:
            return eval_prog(prog.subformula2, env, vars_to_vals)
        return True
    if isinstance(prog, IsAbove):
        if prog.var1 not in vars_to_vals:
            return False
        val1 = vars_to_vals[prog.var1]
        if prog.var2 in vars_to_vals:
            val2 = vars_to_vals[prog.var2]
            return checkIsAbove(val1, val2)
        for obj in env.values():
            if checkMatchingObj(prog.var2, obj):
                return checkIsAbove(val1, obj)
    if isinstance(prog, IsLeft):
        if prog.var1 not in vars_to_vals:
            return False
        val1 = vars_to_vals[prog.var1]
        if prog.var2 in vars_to_vals:
            val2 = vars_to_vals[prog.var2]
            return checkIsLeft(val1, val2)
        for obj in env.values():
            if checkMatchingObj(prog.var2, obj):
                if checkIsLeft(val1, obj):
                    return True
            return False
    if isinstance(prog, IsInside):
        if prog.var1 not in vars_to_vals:
            return False
        val1 = vars_to_vals[prog.var1]
        if prog.var2 in vars_to_vals:
            val2 = vars_to_vals[prog.var2]
            return is_contained(val1["Loc"], val2["Loc"])
        for obj in env.values():
            if checkMatchingObj(prog.var2, obj):
                if is_contained(val1["Loc"], obj["Loc"]):
                    return True
            return False
    if isinstance(prog, IsNextTo):
        if prog.var1 not in vars_to_vals:
            return False
        val1 = vars_to_vals[prog.var1]
        if prog.var2 in vars_to_vals:
            val2 = vars_to_vals[prog.var2]
            for i in range(1, 5):
                if (
                    val1["ObjPosInImgLeftToRight"] == val2["ObjPosInImgLeftToRight"] + i
                    or val1["ObjPosInImgLeftToRight"]
                    == val2["ObjPosInImgLeftToRight"] - i
                ):
                    return True
            return False
        for obj in env.values():
            for i in range(1, 5):
                if checkMatchingObj(prog.var2, obj):
                    if (
                        val1["ObjPosInImgLeftToRight"]
                        == obj["ObjPosInImgLeftToRight"] + i
                        or val1["ObjPosInImgLeftToRight"]
                        == obj["ObjPosInImgLeftToRight"] - i
                    ):
                        return True
            return False


def test_interpreter():
    tests = [
        (
            ForAll(
                "x",
                Exists(
                    "y",
                    And(
                        Is("y", "bicycle"), IfThen(Is("x", "person"), IsAbove("x", "y"))
                    ),
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/9127573526_1e2be02f74_c.jpg",
            True,
        ),
        (
            ForAll(
                "x",
                Exists(
                    "y",
                    And(
                        Is("y", "bicycle"), IfThen(Is("x", "person"), IsAbove("x", "y"))
                    ),
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/3000363792_ded885dd2f_c.jpg",
            False,
        ),
        (
            ForAll(
                "x",
                Exists(
                    "y",
                    And(
                        Is("y", "bicycle"), IfThen(Is("x", "person"), IsAbove("x", "y"))
                    ),
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/6708503525_870ea33fd2_c.jpg",
            False,
        ),
        (
            ForAll(
                "x",
                Exists(
                    "y",
                    And(
                        Is("y", "bicycle"), IfThen(Is("x", "person"), IsAbove("x", "y"))
                    ),
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/15598753673_331ea65b54_c.jpg",
            False,
        ),
        (
            Exists("x", And(Is("x", "face"), Not(Is("x", "smilingFace")))),
            "wedding2",
            "image-eye-web/public/images/wedding2/gabe-and-lauras-wedding_35270215320_o Large.jpeg",
            False,
        ),
        (
            Exists("x", And(Is("x", "face"), Not(Is("x", "smilingFace")))),
            "wedding2",
            "image-eye-web/public/images/wedding2/gabe-and-lauras-wedding_35270215520_o Large.jpeg",
            True,
        ),
        (
            Exists(
                "x",
                Exists(
                    "y", And(Is("y", "person"), And(Is("x", "car"), IsInside("y", "x")))
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/15598753673_331ea65b54_c.jpg",
            True,
        ),
        (
            Exists(
                "x",
                Exists(
                    "y", And(Is("y", "person"), And(Is("x", "car"), IsInside("x", "y")))
                ),
            ),
            "objects",
            "image-eye-web/public/images/objects/6708503525_870ea33fd2_c.jpg",
            False,
        ),
    ]
    for prog, dataset, img, gt in tests:
        img_folder = "image-eye-web/public/images/" + dataset + "/"
        img_to_environment, obj_strs = preprocess(img_folder, 100)
        result = eval_prog(prog, img_to_environment[img]["environment"], {})
        if gt != result:
            print("FAIL")
            print(prog)
            print(img)
            print(gt)
            print(result)
            print()


if __name__ == "__main__":
    test_interpreter()
