from ast import Del
from typing import Union, Literal
from .schemas import Select, Insert, Update, Delete
from pydantic import BaseModel, validator, parse_obj_as, Field


class JsonQuery(BaseModel):
    action: Literal["select", "insert", "update", "delete"]
    query: dict

    def parse(self):
        action = self.action
        if action == "select":
            return parse_obj_as(Select, self.query)
        elif action == "select":
            return parse_obj_as(Insert, self.query)
        elif action == "select":
            return parse_obj_as(Update, self.query)
        elif action == "select":
            return parse_obj_as(Delete, self.query)
        else:
            raise TypeError()

    @classmethod
    def schema_to_json(cls, value):
        action = ""

        if isinstance(value, Select):
            action = "select"
        elif isinstance(value, Insert):
            action = "insert"
        elif isinstance(value, Update):
            action = "update"
        elif isinstance(value, Delete):
            action = "delete"
        else:
            raise TypeError()

        return {"action": action, "query": value.json()}
