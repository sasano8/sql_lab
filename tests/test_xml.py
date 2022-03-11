import imp
from lib2to3.pgen2 import token
from pkg_resources import yield_lines
from pytest import fixture
from pathlib import Path
import pytest


@fixture
def dir_data(tmpdir, request):
    filename = request.module.__file__
    test_dir = Path(filename).parent / "data"

    # if os.path.isdir(test_dir):
    #     dir_util.copy_tree(test_dir, tmpdir)

    return test_dir


def test_parser(dir_data):
    builder = TreeBuilder.from_xmlfile(dir_data / "xmlschemas.xml")
    tree, ctx = builder.tree, builder.ctx

    print(tree)
    print(ctx)


import xml.etree.ElementTree as et


def convert_xml_to_dict(elm: et.Element):
    if "tag" in elm.attrib:
        raise ValueError()

    if "nodes" in elm.attrib:
        raise ValueError()

    return {
        "tag": elm.tag,
        **elm.attrib,
        "nodes": [convert_xml_to_dict(x) for x in elm],
    }


def replace_element(ctx: dict, elm, rebuilder):
    elm["nodes"] = [replace_element(ctx, x, rebuilder) for x in elm["nodes"]]
    elm = rebuilder(ctx, elm)
    return elm


class TreeBuilder:
    def __init__(self, root: et.Element):
        ctx = self.create_context()
        self.tree = replace_element(ctx, root, self.extract_and_replace)
        self.ctx = self.finalize_context(ctx)

    @classmethod
    def from_xmlfile(cls, path):
        tree = et.parse(path).getroot()
        new_tree = convert_xml_to_dict(tree)
        return cls(new_tree)

    @classmethod
    def from_xml(cls, text):
        tree = et.fromstring(text)
        new_tree = convert_xml_to_dict(tree)
        return cls(new_tree)

    @classmethod
    def from_json(cls, text):
        raise NotImplementedError()

    @classmethod
    def from_sql(cls, text):
        raise NotImplementedError()

    @classmethod
    def create_context(cls):
        return {"VAR_TABLE": []}

    @staticmethod
    def extract_and_replace(ctx: dict, elm):
        if elm["tag"] == "TABLE":
            ctx["VAR_TABLE"].append(elm)
            return {"tag": "VAR_TABLE", "value": elm["value"]}
        else:
            return elm

    @staticmethod
    def finalize_context(ctx: dict):
        ctx["VAR_TABLE"] = {v["value"]: v for v in ctx["VAR_TABLE"]}
        return ctx

    @staticmethod
    def validate_client_request(elm):
        ...

    def rebuild(self):
        ...

    def to_xml(self):
        ...

    def to_json(self):
        ...

    def to_dict(self):
        ...

    def to_sql(self, writer=None):
        ...


# How do I use lxml safely as a web-service endpoint?
# https://lxml.de/FAQ.html
# XMLは外部DTDファイルなどの参照時にfile://などでサーバ側のディレクトリを調べる脆弱性がある
# resolve_entities = False
# コンテンツインジェクションに関してはXPathにはSQLと同じ脆弱性がある
# defusedxmlにはセットアップ例とlxmlラッパーAPIが付属している

SCHEMA = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="SQL">
                <xs:complexType>
                    <xs:sequence>
                        <xs:choice maxOccurs="unbounded">
                            <xs:element ref="SELECT" />
                            <xs:element ref="DELETE" />
                            <xs:element ref="INSERT" />
                            <xs:element ref="UDPATE" />
                        </xs:choice>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>

            <!-- DML, DDL, DCL -->
            <xs:element name="SELECT">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="QUERY" minOccurs="0" maxOccurs="1" />
                        <xs:element ref="RETURNING" minOccurs="0" maxOccurs="1" />
                        <xs:element ref="UNION" minOccurs="0" maxOccurs="unbounded"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="DELETE">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="QUERY" minOccurs="0" maxOccurs="1" />
                        <xs:element ref="RETURNING" minOccurs="0" maxOccurs="1" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="UDPATE">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="QUERY" minOccurs="0" maxOccurs="1" />
                        <xs:element ref="RETURNING" minOccurs="0" maxOccurs="1" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="INSERT" />

            <!-- query -->
            <xs:element name="QUERY">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="FROM" />
                        <xs:element ref="JOIN" minOccurs="0" />
                        <xs:element ref="WHERE" minOccurs="0" />
                        <xs:element ref="GROUPBY" minOccurs="0" />
                        <xs:element ref="ORDERBY" minOccurs="0" />
                        <xs:element ref="LIMIT" minOccurs="0" />
                        <xs:element ref="OFFSET" minOccurs="0" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="FROM">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="QUERYABLE" maxOccurs="unbounded" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="JOIN" />
            <xs:element name="GROUPBY">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="COLUMN" maxOccurs="unbounded" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="WHERE">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="EXPRESSION" minOccurs="0" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="HAVING">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="EXPRESSION" minOccurs="0" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="LIMIT" type="xs:integer" />
            <xs:element name="OFFSET" type="xs:integer" />
            <xs:element name="ORDERBY" />
            <xs:element name="RETURNING">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="EXPRESSION" minOccurs="0" maxOccurs="unbounded" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="UNION" />

            <!-- other -->
            <xs:group name="IDENTIFIER">
            </xs:group>

            <xs:element name="IDENTIFIERS">
            </xs:element>

            <xs:group name="QUERYABLE">
                <xs:choice>
                    <xs:element ref="TABLE" />
                    <xs:element ref="SELECT" />
                </xs:choice>
            </xs:group>

            <xs:group name="SELECTABLE">
                <xs:choice>
                    <xs:element ref="COLUMN" />
                    <xs:element ref="JSON" />
                    <xs:element ref="ALIAS" />
                    <xs:element ref="FUNC" />
                    <xs:group ref="OP" />
                </xs:choice>
            </xs:group>

            <xs:group name="ORDER">
                <xs:choice>
                    <xs:element ref="ASC" />
                    <xs:element ref="DESC" />
                </xs:choice>
            </xs:group>

            <xs:group name="EXPRESSION">
                <xs:choice>
                    <xs:element ref="JSON" />
                    <xs:element ref="TABLE" />
                    <xs:element ref="COLUMN" />
                    <xs:element ref="ALIAS" />
                    <xs:element ref="FUNC" />
                    <xs:group ref="OP" />
                </xs:choice>
            </xs:group>
            <xs:element name="TABLE" />
            <xs:element name="COLUMN" />
            <xs:element name="ALIAS" />
            <xs:element name="FUNC" />
            <xs:element name="JSON">
                <xs:simpleType>
                    <xs:restriction base="xs:string">
                        <xs:minLength value="1" />
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="ASC">
                <xs:complexType>
                    <xs:choice>
                        <xs:element ref="ALIAS" />
                        <xs:element ref="COLUMN" />
                    </xs:choice>
                </xs:complexType>
            </xs:element>
            <xs:element name="DESC">
                <xs:complexType>
                    <xs:choice>
                        <xs:element ref="ALIAS" />
                        <xs:element ref="COLUMN" />
                    </xs:choice>
                </xs:complexType>
            </xs:element>

            <!-- operator -->
            <xs:group name="OP">
                <xs:choice>
                    <xs:element ref="AND" />
                    <xs:element ref="OR" />
                </xs:choice>
            </xs:group>
            <xs:element name="EXISTS">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element ref="SELECT"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="AND">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="EXPRESSION" maxOccurs="unbounded" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            <xs:element name="OR">
                <xs:complexType>
                    <xs:sequence>
                        <xs:group ref="EXPRESSION" maxOccurs="unbounded" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>

            <!--
            CAST
            CASE
            WHEN
            IF
            -->
        </xs:schema>
        """


@fixture
def get_parser():
    from lxml import etree

    schema_root = etree.XML(SCHEMA)
    op_root = [
        x
        for x in schema_root.findall("{http://www.w3.org/2001/XMLSchema}group")
        if x.attrib["name"] == "OP"
    ][0]
    operators = op_root.findall("{http://www.w3.org/2001/XMLSchema}choice")[0]
    operators.append(etree.Element("element", dict(name="EQ"), nsmap="xs"))

    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    set_custom_parser(parser)
    return parser


def set_custom_parser(parser):
    from lxml import etree
    import json

    class hook(etree.ElementBase):
        @property
        def value(self):
            if hasattr(self, "_value"):
                return self._value  # type: ignore
            else:
                self._value = json.loads(self.text)
                return self._value

    parser_lookup = etree.ElementDefaultClassLookup(element=hook)
    parser.set_element_class_lookup(parser_lookup)


@fixture
def parse(get_parser):
    from lxml import etree

    def parse(xml):
        s = "<SQL>" + xml + "</SQL>"
        return xml, etree.fromstring(s, parser=get_parser)

    return parse


def escape_for_xml(obj):
    from html import escape, unescape
    from typing import Mapping, Iterable

    if isinstance(obj, str):
        return escape(obj, quote=False)
    elif isinstance(obj, Mapping):
        return {escape_for_xml(k): escape_for_xml(v) for k, v in obj.items()}
    elif isinstance(obj, Iterable):
        return [escape_for_xml(x) for x in obj]

    return obj


def dumps(obj):
    import json

    obj = escape_for_xml(obj)
    return json.dumps(obj, ensure_ascii=False)


def test_escape():
    data = {
        "lt": "<",
        "gt": ">",
        "and": "&",
        "lt2": "&lt;",
        "<": "lt3",
        "single_quote": "'",
        "double_quote": '"',
    }

    escaped = escape_for_xml(data)
    json_str = dumps(data)
    assert escaped == {
        "lt": "&lt;",
        "gt": "&gt;",
        "and": "&amp;",
        "lt2": "&amp;lt;",
        "&lt;": "lt3",
        "single_quote": "'",
        "double_quote": '"',
    }
    assert (
        json_str
        == '{"lt": "&lt;", "gt": "&gt;", "and": "&amp;", "lt2": "&amp;lt;", "&lt;": "lt3", "single_quote": "\'", "double_quote": "\\""}'
    )


def test_escape_xml():
    import json
    from lxml import etree

    data = {
        "lt": "<",
        "gt": ">",
        "and": "&",
        "lt2": "&lt;",
        "<": "lt3",
        "single_quote": "'",
        "double_quote": '"',
    }

    json_str = dumps(data)

    tree = etree.fromstring(f"<TAG>{json_str}</TAG>")
    assert json.loads(tree.text) == data


def test_validate_schema_select(parse):
    import json

    data = {
        "lt": "<",
        "gt": ">",
        "and": "&",
        "lt2": "&lt;",
        "<": "lt3",
        "single_quote": "'",
        "double_quote": '"',
    }

    json_str = dumps(data)

    xml, tree = parse(
        f"<SELECT><QUERY><FROM><TABLE>users1</TABLE><TABLE>users2</TABLE></FROM><WHERE><AND><JSON>{json_str}</JSON><JSON>1</JSON></AND></WHERE><LIMIT>0</LIMIT><OFFSET>0</OFFSET></QUERY><UNION /><UNION /></SELECT>"
    )
    assert json.loads(tree.find(".//JSON").text) == data
    assert tree.find(".//JSON").value == data


def test_validate_single(parse):
    from lxml.etree import XMLSyntaxError

    with pytest.raises(XMLSyntaxError, match="Element 'SQL': Missing child element"):
        xml, tree = parse("")

    xml, tree = parse("<SELECT></SELECT>")
    xml, tree = parse("<DELETE></DELETE>")
    xml, tree = parse("<UDPATE></UDPATE>")
    xml, tree = parse("<INSERT></INSERT>")

    with pytest.raises(
        XMLSyntaxError, match="Element 'NG': This element is not expected."
    ):
        xml, tree = parse("<NG></NG>")

    with pytest.raises(XMLSyntaxError, match="is not expected"):
        xml, tree = parse("<FROM></FROM>")


def test_validate_complex(parse):
    from lxml.etree import XMLSyntaxError

    xml = ""
    xml, tree = parse(xml + "<SELECT></SELECT>")
    xml, tree = parse(xml + "<SELECT></SELECT>")
    xml, tree = parse(xml + "<DELETE></DELETE>")


import sqlparse
from sqlparse.sql import Statement, Token, Where, Having, Case, Function, IdentifierList
from sqlparse.tokens import (
    DDL,
    DML,
    CTE,
    Keyword,
    _TokenType,
    Whitespace,
    Punctuation,
    Wildcard,
)


def test_sqlparse():
    query = "select name, sum(age), 1 + 1, true and false, a as col1, sum(age) as sum, sum(age) sum from users, groups from users, groups where name = 'bob' and name in (select name from admins) limit 1 offset 1 union select * from countries union all (select * from countries union select ARRAY[1,2] from countries) t1; select 1, null"
    parsed_queries = list(parse_sql(query))
    assert parsed_queries


def parse_sql(query: str):

    parsed_queries = sqlparse.parse(query)
    for token in parsed_queries:
        must_be_stmt(token)
        yield analyze_statement(token)


def must_be_stmt(stmt: Statement):
    if not isinstance(stmt, Statement):
        raise TypeError("SQLの構文ではありません")

    if not stmt.token_first().ttype is DML:
        raise TypeError("DMLである必要があります")

    if stmt.get_type() == "SELECT":
        ...
    elif stmt.get_type() == "DELETE":
        raise NotImplementedError()
    elif stmt.get_type() == "UPDATE":
        raise NotImplementedError()
    elif stmt.get_type() == "INSERT":
        raise NotImplementedError()
    else:
        raise NotImplementedError()


def clean_tokens(tokens):
    for token in tokens:
        if token.ttype is Whitespace:
            ...
        elif token.ttype is Punctuation:
            # if token.normalized == ",":
            #     ...
            if token.normalized == ";":
                ...
            else:
                yield token
        else:
            yield token


def split_union(stmt: Statement):
    if not (stmt.get_type() == "SELECT" and stmt.tokens[0].normalized == "SELECT"):
        raise TypeError("SELECT文である必要があります")

    current = []  # type: ignore
    tree = [("QUERY", current)]

    for token in clean_tokens(stmt.tokens):
        if token.is_keyword and (
            token.normalized == "UNION"
            or token.normalized == "UNION ALL"
            or token.normalized == "EXCEPT"
        ):
            current = []
            tree.append((token.normalized, current))
        else:
            current.append(token)

    return tree


class SelectStatement(list):
    def append(self, state, tokens):
        if not state in {
            "QUERY",
            "UNION",
            "UNION ALL",
            "EXCEPT",
        }:
            raise TypeError()
        list.append(self, (state, tokens))


class QueryStatement(list):
    def append(self, state, tokens):
        if not state in {
            "COLUMNS",
            "FROM",
            "WHERE",
            "ORDERBY",
            "GROUPBY",
            "HAVING",
            "LIMIT",
            "OFFSET",
        }:
            raise TypeError()
        list.append(self, (state, tokens))


def analyze_statement(token):
    current_state = token
    if isinstance(current_state, Statement):
        if current_state.get_type() == "SELECT":
            splited = split_union(current_state)
            query = []  # type: ignore
            result = ("SELECT", query)
            for state, tokens in splited:
                select = analyze_select_tokens(tokens)
                select = list(unpack_from(combine_columns(select)))
                query.append((state, select))
            return result
        elif current_state.get_type() == "DELETE":
            raise NotImplementedError()
        elif current_state.get_type() == "UPDATE":
            raise NotImplementedError()
        elif current_state.get_type() == "INSERT":
            raise NotImplementedError()
    else:
        raise NotImplementedError()


def combine_columns(select):
    columns = []

    for state, token in select:
        if state == "COLUMNS":
            columns.append(token)
        else:
            break

    def unpack_IdentifierList(columns):
        it = iter(columns)
        try:
            token = next(it)
        except StopIteration:
            return

        if isinstance(token, IdentifierList):
            yield from clean_tokens(token.tokens)
        else:
            yield token

        for token in it:
            if isinstance(token, IdentifierList):
                yield from clean_tokens(token.tokens)
            else:
                yield token

    yield "COLUMNS", list(unpack_IdentifierList(columns))
    # yield "COLUMNS", columns
    for state, token in select[len(columns) :]:
        yield state, token


def unpack_from(select):
    for state, token in select:
        if state == "FROM":
            if isinstance(token, IdentifierList):
                yield state, list(clean_tokens(token.tokens))
            else:
                yield state, token
        else:
            yield state, token


def analyze_select_tokens(tokens, result=None):
    if result is None:
        result = []

    it = iter(tokens)

    while True:
        try:
            current_state = next(it)
        except StopIteration:
            return result

        while current_state:
            if current_state.is_keyword and current_state.normalized == "SELECT":
                state = "COLUMNS"
            elif current_state.is_keyword and current_state.normalized == "FROM":
                state = "FROM"
            elif isinstance(current_state, Where):
                state = "WHERE"
            elif current_state.is_keyword and current_state.normalized == "ORDERBY":
                state = "ORDERBY"
            elif current_state.is_keyword and current_state.normalized == "GROUPBY":
                state = "GROUPBY"
            elif isinstance(current_state, Having):
                state = "HAVING"
            elif current_state.is_keyword and current_state.normalized == "LIMIT":
                state = "LIMIT"
            elif current_state.is_keyword and current_state.normalized == "OFFSET":
                state = "OFFSET"
            elif isinstance(current_state, Statement):
                state = "STATEMENT"
            else:
                result.append(("INVALID", current_state))
                break

            if state in "STATEMENT":
                result.append(analyze_statement(current_state))
                break

            if state in {"WHERE", "HAVING"}:
                result.append((state, list(clean_tokens(current_state.tokens[:1]))))
                break

            for token in it:
                if is_state_changer(token):
                    current_state = token
                    break
                else:
                    result.append((state, token))
            else:
                break
    return result


def is_state_changer(token: Token):
    if token.ttype is DML:
        return "STATEMENT"
    elif token.ttype is Keyword and token.normalized == "FROM":
        return "FROM"
    elif token.ttype is Keyword and token.normalized == "LIMIT":
        return "LIMIT"
    elif token.ttype is Keyword and token.normalized == "OFFSET":
        return "OFFSET"
    elif isinstance(token, (Where, Having)):
        return True
    else:
        return False


def get_state():
    "DML SELECT"
    "Punctuation ("
    "Punctuation )"


def get_op():
    "Punctuation ("
    "Punctuation )"
    "Keyword and"
    "Comparison ="
    "Comparison in"


def get_func():
    "Name + ( )"


# flatにするとIdentifier(alias)などの解析が大変
def test_parse2():
    query = "select name, sum(age), 1 + 1, true and false, a as col1, sum(age) as sum, sum(age) sum from users, groups from users, groups where name = 'bob' and name in (select name from admins) limit 1 offset 1 union select * from countries union all (select * from countries union select ARRAY[1,2] from countries) t1; select 1, null"
    parsed = sqlparse.parse(query)
    tokens = list(analyze_sql(parsed))
    assert tokens


def analyze_sql(parsed_query):
    for parsed in parsed_query:
        it = clean_tokens2(parsed.flatten())
        # it = map_keywords(it)
        # it = map_values(it)
        # it = map_op(it)
        # it = resolve_builtins(it)
        yield list(it)


class As:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"<As {self.value}>"


class Value:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value is None:
            return str(None)
        else:
            return str(self.value)

    def __repr__(self):
        return f"<Value {str(self)}>"


class OP:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"<OP {self.value}>"


class Func:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"<Func {self.value}>"


def clean_tokens2(tokens):
    for token in tokens:
        if token.ttype is Whitespace:
            ...
        elif token.ttype is Punctuation:
            if token.normalized == ";":
                ...
            else:
                yield token
        else:
            yield token


def map_keywords(tokens):
    for token in tokens:
        if token.ttype is Keyword:
            if token.normalized == "TRUE":
                yield Value(True)
            elif token.normalized == "FALSE":
                yield Value(False)
            elif token.normalized == "NULL":
                yield Value(None)
            else:
                yield token.normalized
        elif token.ttype is Wildcard:
            yield token.normalized
        elif token.ttype is Punctuation:
            yield token.normalized
        else:
            yield token


def map_values(tokens):
    for token in tokens:
        if isinstance(token, (str, Value, OP)):
            yield token
        elif str(token.ttype) == "Token.Literal.Number.Integer":
            yield Value(int(token.value))
        elif str(token.ttype) == "Token.Literal.String.Single":
            yield Value(str(token.value))
        else:
            yield token


def map_op(tokens):
    for token in tokens:
        if isinstance(token, (str, Value, OP)):
            yield token
        elif str(token.ttype) == "Token.Operator.Comparison":
            yield OP(str(token.value))
        elif str(token.ttype) == "Token.Operator":
            yield OP(str(token.value))
        elif str(token.ttype) == "Token.Name.Builtin":
            if token.value == "ARRAY":
                yield "ARRAY"
            else:
                raise NotImplementedError()
        else:
            yield token


def resolve_builtins(tokens):
    for token in tokens:
        if isinstance(token, (str, Value, OP)):
            yield token
        elif str(token.ttype) == "Token.Name":
            if token.normalized == "sum":
                yield Func(token.normalized)
            else:
                yield token
        else:
            yield token


# https://en.wikipedia.org/wiki/SQL_reserved_words
# https://www.postgresql.org/docs/13/sql-keywords-appendix.html

PG_13_RESERVED = {
    "SELECT",
    "DELETE",
    "UPDATE",
    "INSERT",
    "FROM",
    "WHERE",
    "LIMIT",
    "OFFSET",
    "GROUPBY",
    "ORDERBY",
    "HAVING",
    "UNION",
    "UNION ALL",
    "EXCEPT",
    "DISTINCT",
}


def test_separete_semicoron():
    from sqlengine import separete_semicoron

    result = separete_semicoron(
        """part 1;"this is ; part 2;";'this is ; part 3';part 4;this "is ; part" 5;"""
    )

    assert result[0] == "part 1"
    assert result[1] == '"this is ; part 2;"'
    assert result[2] == "'this is ; part 3'"
    assert result[3] == "part 4"
    assert result[4] == 'this "is ; part" 5'


def test_parse():
    from sqlengine import parse
    from sqlengine.parser import value_normalizer

    # query = "select name, sum(age), 1 + 1, true and false, a as col1, sum(age) as sum, sum(age) sum from users, groups from users, groups where name = 'bob' and name in (select name from admins) limit 1 offset 1 union select * from countries union all (select * from countries union select ARRAY[1,2] from countries) t1; select 1, null"
    # query = "select name, sum(age), 1 + 1, true and false, 1 from users"
    query = "select name, 'name', 1 from users union select name, 'name' from users, groups where age = 'name'"
    query = "select * from users where name = 'name' and name = 'name' group by name order by name offset 0 limit 1; select * union select 1"
    query = "select sum(1) sum from users t1"

    assert parse("select 1", normalizer=None) == [{"select": {"value": 1}}]
    assert parse("select '1'", normalizer=None) == [
        {"select": {"value": {"literal": "1"}}}
    ]
    assert parse("select ARRAY[1,2]", normalizer=None) == [
        {"select": {"value": {"create_array": [1, 2]}}}
    ]
    assert parse("select 1 c1", normalizer=None) == [
        {"select": {"name": "c1", "value": 1}}
    ]
    assert parse("select '1' c1", normalizer=None) == [
        {"select": {"name": "c1", "value": {"literal": "1"}}}
    ]
    assert parse("select name", normalizer=None) == [{"select": {"value": "name"}}]
    assert parse("select ARRAY[1,2]", normalizer=None) == [
        {"select": {"value": {"create_array": [1, 2]}}}
    ]
    assert parse("select ARRAY[1,2] c1", normalizer=None) == [
        {"select": {"name": "c1", "value": {"create_array": [1, 2]}}}
    ]
    assert parse(
        "select 1 from users where name = 'bob' offset 0 limit 1", normalizer=None
    ) == [
        {
            "select": {"value": 1},
            "from": "users",
            "where": {"eq": ["name", {"literal": "bob"}]},
            "limit": 1,
            "offset": 0,
        }
    ]

    assert parse(
        "select 1 from provenance.users t1 where name = 'bob' offset 0 limit 1",
        normalizer=None,
    ) == [
        {
            "select": {"value": 1},
            "from": {"value": "provenance.users", "name": "t1"},
            "where": {"eq": ["name", {"literal": "bob"}]},
            "limit": 1,
            "offset": 0,
        }
    ]

    assert parse("select 1", normalizer=value_normalizer) == [
        {"select": {"value": {"literal": 1}}}
    ]

    # assert parse("select '1'") == [{"select": {"value": {"literal": "1"}}}]
    # assert parse("select ARRAY[1, 2]") == [
    #     {"select": {"value": {"create_array": [1, 2]}}}
    # ]
    # assert parse("select 1 col1") == [{"select": [{"as": [{"literal": 1}, "col1"]}]}]
    # assert parse("select 1 as col1") == [{"select": [{"as": [{"literal": 1}, "col1"]}]}]

    query = "select *, c1 from users t1, groups where name = 'name' and name = 1 group by name order by name offset 0 limit 1; select * union select 1"
    assert parse(query, normalizer=None) == [
        {
            "from": [{"value": "users", "name": "t1"}, "groups"],
            "groupby": {"value": "name"},
            "limit": 1,
            "offset": 0,
            "orderby": {"value": "name"},
            "select": ["*", {"value": "c1"}],
            "where": {
                "and": [
                    {"eq": ["name", {"literal": "name"}]},
                    {"eq": ["name", 1]},
                ]
            },
        },
        {"union": [{"select": "*"}, {"select": {"value": 1}}]},
    ]

    select = {
        "from": [{"value": "users", "name": "t1"}, "groups"],
        "groupby": {"value": "name"},
        "limit": 1,
        "offset": 0,
        "orderby": {"value": "name"},
        "select": ["*", {"value": "c1"}],
        "where": {
            "and": [
                {"eq": ["name", {"literal": "name"}]},
                {"eq": ["name", 1]},
            ]
        },
    }

    def normalize_select(select):
        if not (isinstance(select, dict) and "select" in select):
            raise RuntimeError()

        def n_from(_from):
            if isinstance(_from, str):
                yield from ({"value": _from},)
            else:
                for selectable in _from:
                    if isinstance(selectable, str):
                        yield {"value": selectable}
                    else:
                        yield selectable

        select["select"] = list(n_from(select.get("select", [])))
        select["from"] = list(n_from(select.get("from", [])))
        select["groupby"] = list(n_from(select.get("groupby", [])))
        select["orderby"] = list(n_from(select.get("orderby", [])))
        select["having"] = list(n_from(select.get("having", [])))
        return select

    assert normalize_select(select) == {
        "from": [{"value": "users", "name": "t1"}, {"value": "groups"}],
        "groupby": [{"value": "value"}],
        "limit": 1,
        "offset": 0,
        "orderby": [{"value": "value"}],
        "select": [{"value": "*"}, {"value": "c1"}],
        "where": {"and": [{"eq": ["name", {"literal": "name"}]}, {"eq": ["name", 1]}]},
        "having": [],
    }

    query = "select 1 + 1"
    assert parse(query, normalizer=None) == [{"select": {"value": {"add": [1, 1]}}}]

    query = "select 1 + 1 as col order by col asc"
    assert parse(query, normalizer=None) == [
        {
            "select": {"value": {"add": [1, 1]}, "name": "col"},
            "orderby": {"value": "col", "sort": "asc"},
        }
    ]


def test_stmt_normalizer():
    from sqlengine import parse
    from sqlengine.parser import stmt_normalizer

    query = "select *, c1 from users t1, groups where name = 'name' and name = 1 group by name order by name offset 0 limit 1"
    assert parse(query, stmt_normalizer) == [
        {
            "from": [{"value": "users", "name": "t1"}, {"value": "groups"}],
            "groupby": [{"value": "name"}],
            "limit": 1,
            "offset": 0,
            "orderby": [{"value": "name"}],
            "select": [{"value": "*"}, {"value": "c1"}],
            "where": {
                "and": [{"eq": ["name", {"literal": "name"}]}, {"eq": ["name", 1]}]
            },
            "having": [],
        }
    ]

    query = "select name from users group by name order by name"
    assert parse(query, stmt_normalizer) == [
        {
            "from": [{"value": "users"}],
            "groupby": [{"value": "name"}],
            "having": [],
            "orderby": [{"value": "name"}],
            "select": [{"value": "name"}],
        }
    ]

    query = "select 'a'"
    assert parse(query, stmt_normalizer) == [
        {
            "from": [],
            "groupby": [],
            "having": [],
            "orderby": [],
            "select": [{"value": {"literal": "a"}}],
        }
    ]


def test_subquery():
    from sqlengine import parse
    from sqlengine.parser import stmt_normalizer

    query = "select * from (select 1) "
    assert parse(query, stmt_normalizer) == [
        {
            "returning": [{"value": "*"}],
            "from": [{"select": {"value": 1}}],
            "groupby": [],
            "orderby": [],
            "having": [],
        }
    ]

    query = "select * union select 1 union all select 1"
    assert parse(query, stmt_normalizer) == [
        [
            {
                "returning": [{"value": "*"}],
                "from": [],
                "groupby": [],
                "orderby": [],
                "having": [],
            },
            {
                "returning": [{"value": 1}],
                "from": [],
                "groupby": [],
                "orderby": [],
                "having": [],
            },
        ]
    ]
