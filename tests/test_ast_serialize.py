import json
from json import JSONEncoder

from parse import parse
from tex_ast import serialization

def test_serialize_ast_expression():
    expression = parse.ASTExpression(children=[])

    json_str = serialization.ASTExpressionEncoder().encode(expression)
    json_dict  = json.loads(json_str)

    assert json_dict == { 'type': 'ASTExpression', 'children': [] }