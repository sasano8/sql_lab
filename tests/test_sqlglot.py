def test_objects():
    from sqlengine.parser_sqlglot import SqlAnalyzer, quote_ident

    analyzer = SqlAnalyzer(
        """SELECT users.name, app.myfunc(1), myfunc(1) from app.users as users where users.name == 'bob'
        """
    )
    info = analyzer.analyze()

    def create_new_info(info):
        for x in info:
            if x["type"] == "table":
                x["replace"] = "(select * from " + quote_ident("pm2.5") + ")"
                yield x
            else:
                yield x

    new_info = list(create_new_info(info))
    new_sql = analyzer.rebuild_sql(new_info)
    assert new_sql == ""


def test_parse_url():
    from urllib.parse import urlparse

    o = urlparse("ddc://localhost:ddc_domingo")
    assert o