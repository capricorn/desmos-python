from parse import parse
from parse import lex

def test_parse_number():
    tokens = lex.lex('5\\cdot 3')
    number = parse.parse_number(tokens)

    assert len(number.remainder) == len(tokens)-1
    assert isinstance(number.result, parse.ASTNumber)
    assert number.result.number == 5

def test_parse_variable():
    tokens = lex.lex('x+3')
    var = parse.parse_variable(tokens)

    assert isinstance(var.result, parse.ASTVar)
    assert var.result.name == 'x'

def test_parse_infix_binary_op():
    tokens = lex.lex('5+3')
    ast = parse.parse_infix_binary_op(tokens)

    op = ast.result

    assert isinstance(op, parse.ASTBinaryOp)
    assert op.type == parse.ASTBinaryOp.Type.ADD
    assert isinstance(op.left_arg, parse.ASTNumber)
    assert isinstance(op.right_arg, parse.ASTNumber)

def test_binary_op_python_str():
    tokens = lex.lex('5+3')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    # TODO: Preserve int as int
    assert op.python == '(5.0+3.0)'

def test_binary_op_with_vars_python_str():
    tokens = lex.lex('x+y')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    # TODO: Preserve int as int
    assert op.python == '(x+y)'

def test_binary_op_lambda_str():
    tokens = lex.lex('x+y')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    # TODO: Preserve int as int
    assert op.python_func == 'lambda x,y: (x+y)'

def test_binary_op_vars():
    tokens = lex.lex('x+y')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    assert op.vars == ['x','y']

def test_binary_op_nested():
    tokens = lex.lex('x+y+5+z')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    assert op.python_func == 'lambda x,y,z: (x+(y+(5.0+z)))'