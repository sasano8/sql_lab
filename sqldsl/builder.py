from .schemas import Table, SelectSchema, WhereSchema


def table(name: str) -> Table:
    return Table(name=name)


class Select:
    def __init__(self, target):
        self.query = self._init(target)

    def _chain(self, **kwargs):
        dic = self.query.dict()
        dic.update(**kwargs)
        return Select(SelectSchema(**dic))

    def _init(self, target):
        if isinstance(target, str):
            target = Table(name=target)

        if isinstance(target, Table):
            return SelectSchema(from_=target.name)
        elif isinstance(target, SelectSchema):
            return SelectSchema(from_=target)
        else:
            raise TypeError()

    def select(self, *columns):
        if not len(columns):
            raise ValueError()

        return self._chain(returning=columns)

    def select_all(self):
        return self._chain(returning=["*"])

    def where(self, *args, **kwargs):
        where = WhereSchema.create(*args, **kwargs)
        return self._chain(where=where)

    def to_dict(self):
        return {"action": "select", "query": self.query.dict(exclude_unset=True)}
