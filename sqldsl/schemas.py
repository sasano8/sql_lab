from select import select
from typing import Optional, List, Tuple, Union
from unicodedata import name
from pydantic import BaseModel, validator

# https://github.com/adamlouis/squirrelbyte

"""
[
  "select": {
    "columns": [ ... json logic expressions ... ],
    "where": json logic expression,
    "group_by": [ ... json logic expressions ... ],
    "order_by": [ ... json logic expressions ... ],
    "limit": 1000
  }
]
"""

RETURN_ALL = None
RETURN_NONE = None


forward_refs = []


def mark(typ):
    global forward_refs
    forward_refs.append(typ)
    return typ


class Statement(BaseModel):
    def _pipe(self, base: "Base"):
        ...


class Identifier(BaseModel):
    ...


@mark
class Table(Identifier):
    name: str

    def select(self, *columns):
        from_ = SelectSchema.create(self)
        return from_.select(*columns)

    def insert(self, *columns):
        if not len(columns):
            columns = None

        return Insert(table=self.name, columns=columns)

    def update(self):
        return Update(table=self.name)

    def delete(self):
        return SelectSchema(table=self.name)


@mark
class Column(Identifier):
    name: str


@mark
class Columns(Identifier):
    columns: List[str] = None


@mark
class From(Statement):
    query: Union[str, Table, "SelectSchema"]

    @validator("query")
    def str_to_table(cls, v):
        if isinstance(v, str):
            return Table(name=v)
        else:
            return v


@mark
class SelectSchema(Statement):
    from_: Union["SelectSchema", Table, None]
    returning: List[str] = RETURN_ALL
    where: "WhereSchema" = None
    join: str = None
    group_by: str = None
    order_by: str = None
    offset: Optional[int] = None
    limit: Optional[int] = None

    def select(self, *columns):
        if not len(columns):
            columns = None

        dic = self.dict()
        dic.update(returning=columns)
        return SelectSchema(**dic)

    def where(self, *args, **kwargs):
        where = WhereSchema.create(*args, **kwargs)
        dic = self.dict()
        dic.update(where=where)
        return SelectSchema(**dic)


@mark
class Insert(Statement):
    table: str
    returning: List[str] = RETURN_NONE
    values: Union[List[Tuple], SelectSchema]


@mark
class Update(Statement):
    table: From
    returning: List[str] = RETURN_NONE


@mark
class Delete(Statement):
    table: From
    returning: List[str] = RETURN_NONE


@mark
class WhereSchema(Statement):
    @classmethod
    def create(cls, *args, **kwargs):
        ...


@mark
class Join(Statement):
    ...


for typ in forward_refs:
    typ.update_forward_refs()
