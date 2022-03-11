class Operator:
    def __getattr__(self, name):
        return Column(name)

    def __getitem__(self, name):
        return Column(name)


op = Operator()


class UnaryOperator:
    """インクリメントや符号反転など"""

    ...


class Column:
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias

    def __eq__(self, v):
        return {"==": (self.name, v)}

    def __ne__(self, v):
        return {"!=": (self.name, v)}

    def __lt__(self, v):
        return {"<": (self.name, v)}

    def __le__(self, v):
        return {"<=": (self.name, v)}

    def __gt__(self, v):
        return {">": (self.name, v)}

    def __ge__(self, v):
        return {">=": (self.name, v)}

    def in_(self, *args):
        return {"in": (self.name, args)}

    def __add__(self, v):
        return {"+": (self.name, v)}


def where(*operators):
    return {"and": list(operators)}


def or_(*operators):
    return {"or": list(operators)}


cond = where(
    op.name == "aaa",
    15 < op.age,
    op.age < 30,
    op.age.in_(25, 30, 35),
    or_(op.name == "yamada", op.name == "takahashi"),
)
import pprint

pprint.pprint(cond)


"""
builder -> python object -> json -> python object -> resolve

"""
