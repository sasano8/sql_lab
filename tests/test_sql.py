import json


def test_table():
    from json_logic import builder

    a = builder.Select("aa")

    a = builder.Table("users")
    a = a.where(name="aaa")

    print(str(a.__root__))
    assert a


def test_key_value():
    from typing import Any, NamedTuple, Tuple

    from pydantic import parse_obj_as

    class KeyValue(NamedTuple):
        key: str
        values: Any

    operators = {"and": KeyValue}

    def restore(key: str, value):
        cls = operators[key]
        return parse_obj_as(cls, (key, value))

    obj = restore("and", 1)
    assert obj == ("a", 1)


def test_aa():
    class KeyValuePair(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if not len(self) == 1:
                raise ValueError(f"Must be 1 element.")

            key = next(iter(self))
            if not isinstance(key, str):
                raise ValueError(f"Key must be a string.")

    KeyValuePair({"var": 1})

    from pydantic import BaseModel

    class A(BaseModel):
        a: KeyValuePair

    A(a=dict(a=1, b=2, c=3))  # NGにならない


"""
select:
    from:
        table: "users"
    returing:
        distinct: true
        column: "name"
        column: "age"

"""
