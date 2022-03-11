from typing import Tuple, Any, Optional, Union, List, Iterable
from pydantic import BaseModel, validator


undefined = object()


def exclude_undefined(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not undefined}


forward_refs = []


def mark(typ):
    global forward_refs
    forward_refs.append(typ)
    return typ


ops = {}


def name(name: str):
    def wrapper(cls):
        assert name not in ops
        ops[name] = cls
        cls.__name__ = name

        global forward_refs
        forward_refs.append(cls)

        return cls

    return wrapper


class Common:
    @property
    def __name__(self):
        return self.__class__.__name__

    def __eq__(self, v):
        return Eq(__root__=[self, v])

    def __ne__(self, v):
        return Ne(__root__=[self, v])

    def __lt__(self, v):
        return Lt(__root__=[self, v])

    def __le__(self, v):
        return Le(__root__=[self, v])

    def __gt__(self, v):
        return Gt(__root__=[self, v])

    def __ge__(self, v):
        return Ge(__root__=[self, v])

    def in_(self, *args):
        return In(__root__=[self, args])

    def like(self, *args):
        return Like(__root__=[self, args])

    def __add__(self, v):
        return Add(__root__=[self, v])

    # def __add__(self, v):
    #     return Minus(values=[self, v])

    # def __add__(self, v):
    #     return Multi(values=[self, v])

    # def __add__(self, v):
    #     return Division(values=[self, v])

    # def __add__(self, v):
    #     return Remainder(values=[self, v])

    # def __add__(self, v):
    #     return Power(values=[self, v])

    def abs(self, v):
        raise NotImplementedError()


@name("from")
class From(Common, BaseModel):
    __root__: List[Union["Table", "Select"]] = []

    def __str__(self):
        from_ = ",".join(str(x) for x in self.__root__)
        if from_:
            return "FROM " + from_
        else:
            return ""


@name("table")
class Table(Common, BaseModel):
    name: str
    alias: Optional[str] = None

    def __str__(self):
        if self.alias:
            return f"{self.name} AS {self.alias}"
        else:
            return f"{self.name}"


@name("col")
class Column(Common, BaseModel):
    name: str
    alias: Optional[str] = None

    def __str__(self):
        if self.alias:
            return f"{self.name} AS {self.alias}"
        else:
            return f"{self.name}"


@name("select")
class Select(Common, BaseModel):
    from_: From
    distinct: Union[bool, None] = None  # select distinct
    returning: Union[List[str], None] = None
    join: Union[Any, None] = None
    group_by: Union[Any, None] = None
    order_by: Union[Any, None] = None
    offset: Union[int, None] = None
    limit: Union[int, None] = None
    exists: Union[bool, None] = None
    where: Union[Any, None] = None
    union: Union[
        "SelectUnion", "SelectUnionAll", None
    ]  # select * from t1 union all (select * from t2)

    def __str__(self):
        return self._build_str()

    def _build_str(self):
        returning = ",".join(self.returning or [])
        if returning:
            returning = "SELECT " + returning
        else:
            returning = "SELECT *"

        from_ = str(self.from_)
        if self.where is not None:
            where = "WHERE " + str(self.where)
        else:
            where = ""

        return " ".join((returning, from_, where))


@name("union")
class SelectUnion(Select):
    ...


@name("union_all")
class SelectUnionAll(Select):
    ...


class Operator(Common, BaseModel):
    ...


# 単項演算子
class UnaryOperator(Operator):
    __root__: Tuple[Any]


# ２項演算子
class BinaryOperator(Operator):
    __root__: Tuple[Any, Any]


class RootOperator(Operator):
    __root__: List[Operator]


# 算術演算子
# class ArithmeticOperator(Operator):
#     ...


@name("and")
class And(RootOperator):
    ...


@name("or")
class Or(RootOperator):
    ...


@name("is")
class Is(BinaryOperator):
    ...


@name("is_not")
class IsNot(BinaryOperator):
    ...


@name("==")
class Eq(BinaryOperator):
    ...


@name("!=")
class Ne(BinaryOperator):
    ...


@name("<")
class Lt(BinaryOperator):
    ...


@name("<=")
class Le(BinaryOperator):
    ...


@name(">")
class Gt(BinaryOperator):
    ...


@name(">=")
class Ge(BinaryOperator):
    ...


@name("in")
class In(BinaryOperator):
    ...


@name("not_in")
class NotIn(BinaryOperator):
    ...


@name("some")
class Some(BinaryOperator):
    ...


@name("any")
class Any_(BinaryOperator):
    ...


@name("like")
class Like(BinaryOperator):
    ...


@name("not_like")
class NotLike(BinaryOperator):
    ...


@name("between")
class Between(BinaryOperator):
    ...


@name("not_between")
class NotBetween(BinaryOperator):
    ...


@name("+")
class Add(BinaryOperator):
    ...


@name("-")
class Minus(BinaryOperator):
    ...


@name("*")
class Multi(BinaryOperator):
    ...


@name("/")
class Division(BinaryOperator):
    ...


@name("%")
class Remainder(BinaryOperator):
    ...


@name("**")
class Power(BinaryOperator):
    ...


@name("not")
class Not(UnaryOperator):
    ...


@name("min")
class Min(UnaryOperator):
    ...


@name("max")
class Max(UnaryOperator):
    ...


@name("avg")
class Avg(UnaryOperator):
    ...


@name("mean")
class Mean(UnaryOperator):
    ...


@name("count")
class Count(UnaryOperator):
    ...


@name("abs")
class Abs(UnaryOperator):
    ...


@name("unnest")
class Unnest(UnaryOperator):
    ...


for typ in forward_refs:
    typ.update_forward_refs()
