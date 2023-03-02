from semantics import semantics_types
from semantics import semantics_lia
from semantics.semantics_types import InterpretedFunctionBase
from exprs import exprtypes
from eusolver_utils import utils
import z3

if __name__ == '__main__':
    utils.print_module_misuse_and_exit()

class Match(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Match', 2,
        (exprtypes.ImgsType(), exprtypes.StringType()),
        exprtypes.ImgsType())
        self.eval_children = lambda a,b: {item for item in a if b in item[0]}

class Union(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Union', 2,
        (exprtypes.ImgsType(), exprtypes.ImgsType()),
        exprtypes.ImgsType())
        self.eval_children = lambda a,b: a.union(b) 

class Intersect(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Intersect', 2,
        (exprtypes.ImgsType(), exprtypes.ImgsType()),
        exprtypes.ImgsType())
        self.eval_children = lambda a,b: a.intersection(b) 


class Complement(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Complement', 2,
        (exprtypes.ImgsType(), exprtypes.ImgsType()),
        exprtypes.ImgsType())
        self.eval_children = lambda a,b:  a - b

class Find(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Find', 4,
        (exprtypes.ImgsType(), exprtypes.ImgsType(), exprtypes.StringType(), exprtypes.StringType()),
        exprtypes.ImgsType())
        self.eval_children = handle_find

def is_contained(bbox1, bbox2):
    left1, right1, top1, bottom1 = bbox1
    left2, right2, top2, bottom2 = bbox2
    return left1 > left2 and top1 > top2 and bottom1 < bottom2 and right1 < right2

def handle_find(input_, objs, rest, pos):
    mapped_objs = set()
    if pos == 'GetLeft':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_left = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if left > target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left > cur_left:
                    cur_left = left
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetRight':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_left = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if left < target_left:
                    continue
                if bottom < target_top or top > target_bottom:
                    continue
                if cur_left is None or left < cur_left:
                    cur_left = left
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetPrev':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_left = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if left > target_left:
                    continue
                if cur_left is None or left > cur_left:
                    cur_left = left
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetNext':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_left = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if left < target_left:
                    continue
                if cur_left is None or left < cur_left:
                    cur_left = left
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetAbove':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_bottom = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if bottom > target_bottom:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_bottom is None or bottom > cur_bottom:
                    cur_top = top
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetBelow':
        for target_obj in objs:
            target_left, target_right, target_top, target_bottom = target_obj[1], target_obj[2], target_obj[3], target_obj[4]
            target_img = target_obj[5]
            cur_obj = None
            cur_top = None
            for obj in input_:
                if obj == target_obj:
                    continue
                if rest not in obj[0]:
                    continue
                if target_img != obj[5]:
                    continue
                left, right, top, bottom = obj[1], obj[2], obj[3], obj[4]
                if top < target_top:
                    continue
                if right < target_left or left > target_right:
                    continue
                if cur_top is None or top < cur_top:
                    cur_top = top
                    cur_obj = obj
            if cur_obj is not None:
                mapped_objs.add(cur_obj)
    if pos == 'GetParents':
        for target_obj in objs:
            for obj in input_:
                if target_obj[5] != obj[5]:
                    continue
                if rest not in obj[0]:
                    continue
                if obj == target_obj:
                    continue
                if is_contained(target_obj[1:5], obj[1:5]):
                    mapped_objs.add(obj)
    if pos == 'GetChildren':
        for target_obj in objs:
            for obj in input_:
                if target_obj[5] != obj[5]:
                    continue
                if rest not in obj[0]:
                    continue
                if obj == target_obj:
                    continue
                if is_contained(obj[1:5], target_obj[1:5]):
                    mapped_objs.add(obj)
    return frozenset(mapped_objs)


class IMGInstantiator(semantics_types.InstantiatorBase):
    def __init__(self):
        super().__init__('img')
        self.lia_instantiator = semantics_lia.LIAInstantiator()
        self.function_types = {
            'Match': (exprtypes.ImgsType(), exprtypes.StringType()),
            'Union': (exprtypes.ImgsType(), exprtypes.ImgsType()),
            'Intersection': (exprtypes.ImgsType(), exprtypes.ImgsType()),
            'Complement': (exprtypes.ImgsType(), exprtypes.ImgsType()),
            'Find': (exprtypes.ImgsType(), exprtypes.ImgsType(), exprtypes.StringType(), exprtypes.StringType()),
            }
        self.function_instances = {
            'Match': Match(),
            'Union': Union(),
            'Intersection': Intersect(),
            'Complement': Complement(),
            'Find': Find(),
            }

    def _get_canonical_function_name(self, function_name):
        return function_name

    def _do_instantiation(self, function_name, mangled_name, arg_types):
        if function_name not in self.function_types:
            return None
        
        assert arg_types == self.function_types[function_name]
        return self.function_instances[function_name]

        