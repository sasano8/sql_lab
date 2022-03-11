from typing import Iterable, Union
from .operators import (
    Select as _Select,
    Table as _Table,
    Column as _Column,
    From as _From,
)
from .operators import And

undefined = object()


def exclude_undefined(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not undefined}


class Table:
    def __init__(self, name, alias=None):
        self.__root__ = _Table(name=name, alias=alias)

    def select(self, *columns):
        query = From(self.__root__)
        return query.select(*columns)

    def where(self, *args, **kwargs):
        query = From(self.__root__)
        return query.where(*args, **kwargs)


class Column:
    def __init__(self, name, alias=None):
        self.__root__ = _Column(name=name, alias=alias)


class From:
    def __init__(self, *args: Union[str, "Table"]):
        values = list(self._iteritem(args))
        self.__root__ = _From(__root__=values)

    @classmethod
    def _iteritem(cls, args):
        for v in args:
            if isinstance(v, str):
                yield Table(v).__root__
            elif isinstance(v, (Table, From, Select)):
                yield v.__root__
            elif isinstance(v, (_Table, _From, _Select)):
                yield v
            else:
                raise TypeError(f"{v}")

    def select(self, *columns):
        query = Select(from_=self.__root__)
        return query.select(*columns)

    def where(self, *args, **kwargs):
        query = Select(from_=self.__root__)
        return query.where(*args, **kwargs)


class Select:
    def __init__(
        self,
        from_,
        returning=None,
        where=None,
        join=None,
        group_by=None,
        order_by=None,
        offset=None,
        limit=None,
        exists=None,
        union=None,
    ):
        if isinstance(from_, From):
            from_ = from_.__root__
        elif isinstance(from_, _From):
            from_ = from_
        elif isinstance(from_, Iterable):
            if isinstance(from_, str):
                from_ = From(from_).__root__
            else:
                from_ = From(*from_).__root__

        self.__root__ = _Select(
            from_=from_,
            returning=returning,
            where=where,
            join=join,
            group_by=group_by,
            order_by=order_by,
            offset=offset,
            limit=limit,
            exists=exists,
            union=union,
        )

    def __str__(self):
        return str(self.__root__)

    def _chain(
        self,
        returning=undefined,
        where=undefined,
        join=undefined,
        group_by=undefined,
        order_by=undefined,
        offset=undefined,
        limit=undefined,
        exists=undefined,
        union=undefined,
    ):
        update = exclude_undefined(
            returning=returning,
            where=where,
            join=join,
            group_by=group_by,
            order_by=order_by,
            offset=offset,
            limit=limit,
            exists=exists,
            union=union,
        )

        # values = list(self.values)
        # if returning is not undefined:
        #     values[1] = returning

        # if where is not undefined:
        #     values[2] = where

        # if join is not undefined:
        #     values[3] = join

        # if group_by is not undefined:
        #     values[4] = group_by

        # if order_by is not undefined:
        #     values[5] = order_by

        # if offset is not undefined:
        #     values[6] = offset

        # if limit is not undefined:
        #     values[7] = limit

        # if exists is not undefined:
        #     if values[8] is not None:
        #         raise RuntimeError(f"Can't re assignment. Already set {values[8]}")
        #     values[8] = exists

        # if union is not undefined:
        #     values[9] = union

        current = self.__root__.dict(exclude_none=True)
        del current["from_"]

        if "exists" in update:
            if current.exists is not None:
                raise RuntimeError(f"Can't re assignment. Already set {current.exists}")

        current.update(**update)
        from_ = self.__root__.from_
        return self.__class__(from_=from_, **current)

    def select(self, *columns):
        if not len(columns):
            columns = None

        return self._chain(returning=columns)

    def _build_where(self, args, kwargs):
        if not len(args) and not len(kwargs):
            return None
        else:
            kw = list(_Column(name=k) == v for k, v in kwargs.items())
            where = And(__root__=(*args, *kw))
            return where

    def where(self, *args, **kwargs):
        where = self._build_where(args, kwargs)
        if where is None:
            return self
        else:
            return self._chain(where=where)

    def exists(self, *args, **kwargs):
        where = self._build_where(args, kwargs)
        if where is None:
            return self
        else:
            return self._chain(where=where, exists=True)

    def not_exists(self, *args, **kwargs):
        where = self._build_where(args, kwargs)
        if where is None:
            return self
        else:
            return self._chain(where=where, exists=False)