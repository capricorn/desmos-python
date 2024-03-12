import json
from json import JSONEncoder

from parse import parse
from tex_ast import serialization

def test_serialize_ast_expression():
    expression = parse.ASTExpression(children=[])

    json_str = serialization.ASTExpressionEncoder().encode(expression)
    json_dict  = json.loads(json_str)

    assert json_dict == { 'type': 'ASTExpression', 'children': [] }

def test_serialize_var():
    var = parse.ASTVar(children=[], name='x')
    json_str = serialization.ASTVarEncoder().encode(var)
    json_dict = json.loads(json_str)

    assert json_dict == { 'type': 'ASTVar', 'name': 'x' }

def test_serialize_number():
    num = parse.ASTNumber(children=[], number=5)
    json_str = serialization.ASTNumberEncoder().encode(num)
    json_dict = json.loads(json_str)

    assert json_dict == { 'type': 'ASTNumber', 'number': '5' }

def test_serialize_binary_op():
    bin_op = parse.ASTBinaryOp(
        children=[], 
        type=parse.ASTBinaryOp.Type.MULTIPLY,
        left_arg=parse.ASTNumber(children=[], number=5),
        right_arg=parse.ASTNumber(children=[], number=7))

    json_str = serialization.ASTBinaryOpEncoder().encode(bin_op)
    json_dict = json.loads(json_str)

    assert json_dict == { 
        'type': 'ASTBinaryOp',
        'op': '*',
        'left_arg': {
            'type': 'ASTNumber',
            'number': '5'
        },
        'right_arg': {
            'type': 'ASTNumber',
            'number': '7'
        }
    }
