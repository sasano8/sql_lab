from sqlglot import parse_one
import sqlglot.expressions as exp
from functools import partial
import re


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def separete_semicoron(sql: str):
    sql = sql.strip()
    PATTERN = re.compile(r"""((?:[^;"']|"[^"]*"|'[^']*')+)""")
    return [x.strip() for x in PATTERN.split(sql)[1::2]]


def quote_ident(s: str):
    import string

    escape = False
    for c in s:
        if c in string.punctuation:
            escape = True
            break

    if escape:
        if '"' in s:
            raise ValueError("Cant contains dobule quote.")

        return '"' + s + '"'
    else:
        return s


class SqlAnalyzer:
    def __init__(self, sql, dialect="postgres"):
        self.sql = sql
        self.dialect = dialect
        self.tree: exp.Expression

    @staticmethod
    def separete_semicoron(sql: str) -> list:
        sql = sql.strip()
        PATTERN = re.compile(r"""((?:[^;"']|"[^"]*"|'[^']*')+)""")
        return PATTERN.split(sql)[1::2]

    def _parse(self):
        queries = separete_semicoron(self.sql)
        if len(queries) != 1:
            raise RuntimeError("must be one statement.")

        parsed = parse_one(queries[0], read=self.dialect)
        return parsed

    def analyze(self):
        if hasattr(self, "tree"):
            raise RuntimeError("analyze can only be executed once.")

        tree: exp.Expression = self._parse()
        objects = []  # type: ignore
        tree = tree.transform(partial(self._scan, objects=objects), copy=False)
        self.tree = tree
        return objects

    def rebuild_sql(self, objects=[]) -> exp.Expression:
        objects = {dic["id"]: dic for dic in objects}
        tree = self.tree.transform(partial(self._rebuild, objects=objects), copy=False)
        return tree.sql(dialect=self.dialect)

    def _scan(self, node, objects: list):
        if isinstance(node, exp.Func):
            schema = getattr(node.parent, "table", None)
            is_anonymous = isinstance(node, exp.Anonymous)
            objects.append(
                {
                    "id": id(node),
                    "type": "anonymous",
                    "schema": schema.text("this") if schema else None,
                    "ident": node.text("this"),
                    "is_anonymous": is_anonymous,
                    "text": node.text("this"),
                }
            )
        elif isinstance(node, exp.Table):
            schema = node.args.get("db", None)
            objects.append(
                {
                    "id": id(node),
                    "type": "table",
                    "schema": schema.text("this") if schema else None,
                    "ident": node.text("this"),
                    "is_anonymous": False,
                    "text": node.text("this"),
                }
            )
        elif isinstance(node, exp.Column):
            if isinstance(
                node.this, exp.Func
            ):  # schema.func() のとき、schemaはcolumnと認識されているので、その時は無視する
                ...
            else:
                schema = getattr(node, "table", None)
                objects.append(
                    {
                        "id": id(node),
                        "type": "col",
                        "schema": None,
                        "table": schema.text("this") if schema else None,
                        "ident": node.text("this"),
                        "is_anonymous": False,
                        "text": node.text("this"),
                    }
                )
        return node

    def _rebuild(self, node, objects: dict):
        update = objects.get(id(node), None)
        if update:
            replace = update.get("replace", None)
            if replace is None:
                return node
            else:
                return parse_one(replace)
        else:
            return node
