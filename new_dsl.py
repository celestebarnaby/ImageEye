class Formula:
    pass


class ForAll(Formula):
    def __init__(self, var, subformula):
        # I don't think I need the var but let's just keep it here for now
        self.var = var
        self.subformula = subformula

    def __str__(self):
        return type(self).__name__ + "(" + self.var + "," + str(self.subformula) + ")"


class Exists(Formula):
    def __init__(self, var, subformula):
        # I don't think I need the var but let's just keep it here for now
        self.var = var
        self.subformula = subformula

    def __str__(self):
        return type(self).__name__ + "(" + self.var + "," + str(self.subformula) + ")"


class Subformula(Formula):
    pass


class And(Subformula):
    def __init__(self, subformula1, subformula2):
        self.subformula1 = subformula1
        self.subformula2 = subformula2

    def __str__(self):
        return (
            type(self).__name__
            + "("
            + str(self.subformula1)
            + ","
            + str(self.subformula2)
            + ")"
        )


class IfThen(Subformula):
    def __init__(self, subformula1, subformula2):
        self.subformula1 = subformula1
        self.subformula2 = subformula2

    def __str__(self):
        return (
            type(self).__name__
            + "("
            + str(self.subformula1)
            + ","
            + str(self.subformula2)
            + ")"
        )


class Not(Subformula):
    def __init__(self, subformula):
        self.subformula = subformula

    def __str__(self):
        return type(self).__name__ + "(" + str(self.subformula) + ")"


class Predicate(Subformula):
    pass


class Is(Predicate):
    def __init__(self, var1, var2):
        # I don't think I need the var but let's just keep it here for now
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return type(self).__name__ + "(" + self.var1 + "," + self.var2 + ")"


class IsAbove(Predicate):
    def __init__(self, var1, var2):
        # I don't think I need the var but let's just keep it here for now
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return type(self).__name__ + "(" + self.var1 + "," + self.var2 + ")"


class IsLeft(Predicate):
    def __init__(self, var1, var2):
        # I don't think I need the var but let's just keep it here for now
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return type(self).__name__ + "(" + self.var1 + "," + self.var2 + ")"


class IsNextTo(Predicate):
    def __init__(self, var1, var2):
        # I don't think I need the var but let's just keep it here for now
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return type(self).__name__ + "(" + self.var1 + "," + self.var2 + ")"


class IsInside(Predicate):
    def __init__(self, var1, var2):
        # I don't think I need the var but let's just keep it here for now
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return type(self).__name__ + "(" + self.var1 + "," + self.var2 + ")"
