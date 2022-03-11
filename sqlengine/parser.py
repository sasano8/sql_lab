from mo_sql_parsing import parse as _parse
import re


def to_row(tokens):
    columns = list(tokens)
    if len(columns) > 1:
        return {"select": [{"value": v[0]} for v in columns]}
    else:
        return {"select": {"value": columns[0]}}


def separete_semicoron(sql: str):
    PATTERN = re.compile(r"""((?:[^;"']|"[^"]*"|'[^']*')+)""")
    return PATTERN.split(sql)[1::2]


def union_normalizer(stmt):
    ...


def stmt_normalizer(select):
    if isinstance(select, dict):
        if "union" in select:
            result = [stmt_normalizer(x) for x in select["union"]]
            return result
        elif "union all" in select:
            result = [stmt_normalizer(x) for x in select["union all"]]
            return result

        elif "except" in select:
            result = [stmt_normalizer(x) for x in select["except"]]
            return result

        elif "select" in select:
            ...
        else:
            return select
    else:
        return select

    def n_from(_from):
        if isinstance(_from, str):
            yield from ({"value": _from},)
        elif isinstance(_from, dict):
            yield from (_from,)
        else:
            for selectable in _from:
                if isinstance(selectable, str):
                    yield {"value": selectable}
                else:
                    yield selectable

    select["returning"] = list(n_from(select.pop("select", [])))
    select["from"] = list(n_from(select.get("from", [])))
    select["groupby"] = list(n_from(select.get("groupby", [])))
    select["orderby"] = list(n_from(select.get("orderby", [])))
    select["having"] = list(n_from(select.get("having", [])))
    return select


def create_select(select, *unions):
    ...


def value_normalizer(obj):
    if isinstance(obj, dict):
        obj = {k: value_normalizer(v) for k, v in obj.items()}
        obj = normalize_value(obj)
        return obj
    elif isinstance(obj, list):
        return [value_normalizer(x) for x in obj]
    else:
        return normalize_value(obj)


def normalize_value(obj):
    if isinstance(obj, str):
        return {"ident": obj}
    elif isinstance(obj, dict) and "value" in obj:
        if isinstance(obj["value"], (int, float)):
            return obj["value"]
        elif "ident" in obj["value"]:
            val = obj.pop("value")
            obj["ident"] = val["ident"]
            return obj
        else:
            val = obj.pop("value")
            obj["ident"] = val
            return obj
    elif isinstance(obj, dict) and "literal" in obj:
        return obj["literal"]
    else:
        return obj


def normalize_value(obj):
    if (
        isinstance(obj, dict)
        and "value" in obj
        and isinstance(obj["value"], (int, float))
    ):
        obj["value"] = {"literal": obj["value"]}
        return obj
    else:
        return obj


def normalize_recursive(obj):
    if isinstance(obj, dict):
        key = next(iter(obj))

        if key == "value" and len(obj) == 1:
            if is_value(obj[key]):
                return {"literal": obj[key]}
            else:
                if is_literal(obj[key]):
                    return normalize_recursive(obj[key])
                else:
                    if isinstance(obj[key], str):
                        return obj[key]
                    else:
                        return {key: normalize_recursive(obj[key])}
        elif key == "literal":
            if isinstance(obj[key], str):
                return {"literal": f'"{obj[key]}"'}
            else:
                return obj
        elif key in {"select", "union"}:
            return {k: to_list(normalize_recursive(v)) for k, v in obj.items()}
        elif key in {"eq", "ne", "and", "or"}:
            return {key: normalize_recursive(obj[key])}
        elif key == "from":
            if isinstance(obj[key], str):
                return {key: [obj[key]]}
            else:
                return obj
        else:
            if key == "value" and "name" in obj:
                return {"as": [obj["value"], obj["name"]]}
            else:
                if key in {"create_array"}:
                    return obj
                else:
                    raise RuntimeError(obj)

    elif isinstance(obj, list):
        return [normalize_recursive(x) for x in obj]

    else:
        if isinstance(obj, (int, float)):
            return {"literal": obj}
        else:
            return obj


def to_list(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


def unpack_value(obj):
    if isinstance(obj, dict) and "value" in obj:
        return obj["value"]
    else:
        return obj


def is_literal(val):
    if isinstance(val, dict) and "literal" in val:
        return True
    else:
        return False


def is_value(val):
    if isinstance(val, (list, dict)):
        return False
    elif isinstance(val, str):
        return False
    else:
        return True


# def parse(sql: str, normalizer=normalize_recursive):
def parse(sql: str, normalizer=value_normalizer):
    statements = separete_semicoron(sql)
    if normalizer:
        parsed = [normalizer(_parse(query)) for query in statements]
    else:
        parsed = [_parse(query) for query in statements]
    return parsed