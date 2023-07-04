from new_dsl import *
from utils import *
from image_utils import *


def eval_prog(prog, env, vars_to_vals):
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
        if prog.var2 == "face":
            return val["Type"] == "Face"
        elif prog.var2 == "smilingFace":
            return "Smile" in val
        elif prog.var2 == "eyesOpenFace":
            return "EyesOpen" in val
        else:
            return val["Type"] == "Object" and val["Name"].lower() == prog.var2.lower()
    if isinstance(prog, IfThen):
        if_eval = eval_prog(prog.subformula1, env, vars_to_vals)
        if if_eval:
            return eval_prog(prog.subformula2, env, vars_to_vals)
        return True
    if isinstance(prog, IsAbove):
        # TODO: make this more flexible
        if prog.var1 not in vars_to_vals or prog.var2 not in vars_to_vals:
            return False
        val1, val2 = vars_to_vals[prog.var1], vars_to_vals[prog.var2]
        left1, top1, right1, bottom1 = val1["Loc"]
        left2, top2, right2, bottom2 = val2["Loc"]
        center_y_1 = (top1 + bottom1) / 2
        center_y_2 = (top2 + bottom2) / 2
        if right1 < left2 or left1 > right2:
            return False
        return center_y_1 < center_y_2
    if isinstance(prog, IsLeft):
        if prog.var1 not in vars_to_vals or prog.var2 not in vars_to_vals:
            return False
        val1, val2 = vars_to_vals[prog.var1], vars_to_vals[prog.var2]
        left1, top1, right1, bottom1 = val1["Loc"]
        left2, top2, right2, bottom2 = val2["Loc"]
        center_x_1 = (top1 + bottom1) / 2
        center_x_2 = (top2 + bottom2) / 2
        if bottom1 < top2 or top1 > bottom2:
            return False
        return center_x_1 < center_x_2
    if isinstance(prog, IsInside):
        if prog.var1 not in vars_to_vals or prog.var2 not in vars_to_vals:
            return False
        val1, val2 = vars_to_vals[prog.var1], vars_to_vals[prog.var2]
        return is_contained(val1["Loc"], val2["Loc"])
    if isinstance(prog, IsNextTo):
        if prog.var1 not in vars_to_vals or prog.var2 not in vars_to_vals:
            return False
        val1, val2 = vars_to_vals[prog.var1], vars_to_vals[prog.var2]
        return (
            val1["ObjPosInImgLeftToRight"] == val2["ObjPosInImgLeftToRight"] + 1
            or val1["ObjPosInImgLeftToRight"] == val2["ObjPosInImgLeftToRight"] - 1
        )


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
