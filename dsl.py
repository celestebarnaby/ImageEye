import copy
from typing import Any, List, Dict, Set, Tuple


class Node:
    def __str__(self):
        return type(self).__name__

    def __eq__(self, other):
        return isinstance(other, Node)

    def __lt__(self, other):
        self_str = str(self)
        other_str = str(other)
        if self_str == "Hole" and other_str == "Hole":
            return self_str < other_str
        elif self_str == "Hole":
            return False
        elif other_str == "Hole":
            return True
        elif "Hole" in self_str and "Hole" in other_str:
            return self_str < other_str
        elif "Hole" in other_str:
            return True
        elif "Hole" in self_str:
            return False
        return self_str < other_str


class Program(Node):
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return str([str(statement) + "; " for statement in self.statements])

    def duplicate(self):
        new_statements = copy.copy(self.statements)
        return Program(new_statements)


class Statement(Program):
    pass


class ApplyAction(Statement):
    def __init__(self, action, extractor):
        self.action = action
        self.extractor = extractor

    def __str__(self):
        return (
            type(self).__name__
            + "("
            + str(self.action)
            + ", "
            + str(self.extractor)
            + ")"
        )


class Action(Node):
    def __eq__(self, othr):
        return str(self) == str(othr)

    def __hash__(self):
        return hash(str(self))


class Crop(Action):
    pass


class Blur(Action):
    def __init__(self, value=51):
        self.value = value


class Blackout(Action):
    pass


class Sharpen(Action):
    pass


class Brighten(Action):
    def __init__(self, value=30):
        self.value = value


class Recolor(Action):
    def __init__(self, value=100):
        self.value = value


class Extractor(Node):
    def __init__(self, val=None, output_under=None, output_over=None):
        self.val = val
        self.output_under = output_under
        self.output_over = output_over

    def __eq__(self, other):
        return str(self) == str(other)


class Map(Extractor):
    def __init__(
        self,
        extractor: Extractor,
        restriction,
        position,
        val=None,
        output_under=None,
        output_over=None,
    ):
        super().__init__(val, output_under, output_over)
        self.extractor = extractor
        self.restriction = restriction
        self.position = position

    def __str__(self):
        return (
            type(self).__name__
            + "("
            + str(self.extractor)
            + ", "
            + str(self.restriction)
            + ", "
            + str(self.position)
            + ")"
        )

    def duplicate(self):
        return Map(
            self.extractor,
            self.restriction,
            self.position,
            self.val,
            self.output_under,
            self.output_over,
        )

    def __eq__(self, other):
        if not isinstance(other, Map):
            return False
        return (
            self.extractor == other.extractor
            and self.restriction == other.restriction
            and self.position == other.position
        )


class Attribute(Extractor):
    pass


class IsFace(Attribute):
    def duplicate(self):
        return IsFace(self.val, self.output_under, self.output_over)

    def __str__(self):
        return type(self).__name__


class IsText(Attribute):
    def duplicate(self):
        return IsText(self.val, self.output_under, self.output_over)

    def __str__(self):
        return type(self).__name__


class GetFace(Attribute):
    def __init__(self, index: int, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.index = index

    def __str__(self):
        return type(self).__name__ + "(" + str(self.index) + ")"

    def __eq__(self, other):
        if isinstance(other, GetFace):
            return self.index == other.index
        return False

    def duplicate(self):
        return GetFace(self.index, self.val, self.output_under, self.output_over)


class IsObject(Attribute):
    def __init__(self, obj: str, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.obj = obj

    def __str__(self):
        return type(self).__name__ + "(" + str(self.obj) + ")"

    def __eq__(self, other):
        if isinstance(other, IsObject):
            return self.obj == other.obj
        return False

    def duplicate(self):
        return IsObject(self.obj, self.val, self.output_under, self.output_over)


class MatchesWord(Attribute):
    def __init__(self, word: str, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.word = word

    def __str__(self):
        return "MatchesWord(" + str(self.word) + ")"

    def __eq__(self, other):
        if isinstance(other, MatchesWord):
            return self.word == other.word
        return False

    def duplicate(self):
        return MatchesWord(self.word, self.val, self.output_under, self.output_over)


class IsPhoneNumber(Attribute):
    def duplicate(self):
        return IsPhoneNumber(self.val, self.output_under, self.output_over)

    def __str__(self):
        return type(self).__name__


class IsPrice(Attribute):
    def duplicate(self):
        return IsPrice(self.val, self.output_under, self.output_over)

    def __str__(self):
        return type(self).__name__


class IsSmiling(Attribute):
    def duplicate(self):
        return IsSmiling(self.val, self.output_under, self.output_over)

    def __str__(self):
        return "Smile"


class EyesOpen(Attribute):
    def duplicate(self):
        return EyesOpen(self.val, self.output_under, self.output_over)

    def __str__(self):
        return "EyesOpen"


class MouthOpen(Attribute):
    def duplicate(self):
        return MouthOpen(self.val, self.output_under, self.output_over)

    def __str__(self):
        return "MouthOpen"


class BelowAge(Attribute):
    def __init__(self, age: int, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.age = age

    def __str__(self):
        return "BelowAge(" + str(self.age) + ")"

    def __eq__(self, other):
        if isinstance(other, BelowAge):
            return self.age == other.age
        return False

    def duplicate(self):
        return BelowAge(self.age, self.val, self.output_under, self.output_over)


class AboveAge(Attribute):
    def __init__(self, age: int, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.age = age

    def __str__(self):
        return "AboveAge(" + str(self.age) + ")"

    def __eq__(self, other):
        if isinstance(other, AboveAge):
            return self.age == other.age
        return False

    def duplicate(self):
        return AboveAge(self.age, self.val, self.output_under, self.output_over)


class Union(Extractor):
    def __init__(
        self, extractors: List[Extractor], val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractors = extractors

    def __str__(self):
        extractor_strs = [str(extr) for extr in self.extractors]
        return type(self).__name__ + "[" + ", ".join(extractor_strs) + "]"

    def duplicate(self):
        return Union(self.extractors, self.val, self.output_under, self.output_over)

    def __eq__(self, other):
        if isinstance(other, Union):
            return self.extractors == other.extractors
        return False


class Intersection(Extractor):
    def __init__(
        self, extractors: List[Extractor], val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractors = extractors

    def __str__(self):
        extractor_strs = [str(extr) for extr in self.extractors]
        return type(self).__name__ + "[" + ", ".join(extractor_strs) + "]"

    def duplicate(self):
        return Intersection(
            self.extractors, self.val, self.output_under, self.output_over
        )

    def __eq__(self, other):
        if isinstance(other, Intersection):
            return self.extractors == other.extractors
        return False


class Complement(Extractor):
    def __init__(
        self, extractor: Extractor, val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractor = extractor

    def __str__(self):
        return type(self).__name__ + "(" + str(self.extractor) + ")"

    def duplicate(self):
        return Complement(self.extractor, self.val, self.output_under, self.output_over)

    def __eq__(self, other):
        if isinstance(other, Complement):
            return self.extractor == other.extractor
        return False


class Position(Node):
    def __eq__(self, other):
        return type(self) is type(other)


class GetPrev(Position):
    pass


class GetNext(Position):
    pass


class GetLeft(Position):
    pass


class GetRight(Position):
    pass


class GetBelow(Position):
    pass


class GetAbove(Position):
    pass


class GetContains(Position):
    pass


class GetIsContained(Position):
    pass
