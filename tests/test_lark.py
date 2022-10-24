from pprint import pprint


def test_lark():
    from larkparser import parse

    # result = parse("select name from users, users2")
    # result = parse("select schema.name col1 from app.users t1, app.users2 t2")
    # result = parse("select * from app.users")
    # result = parse("select t1.name c1, t1.name c2 from app.users t1")
    # result = parse("select myschema.myfunc(1)")  # 関数呼び出しに対応していない
    result = parse('select * from "mytable"')  # 関数呼び出しに対応していない
    print(result.pretty())
    assert result