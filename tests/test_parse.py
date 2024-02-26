import pytest

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
    assert op.python_func_str == 'lambda x,y: (x+y)'

def test_binary_op_vars():
    tokens = lex.lex('x+y')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    assert op.vars == ['x','y']

def test_binary_op_nested():
    tokens = lex.lex('x+y+5+z')
    ast = parse.parse_infix_binary_op(tokens)
    op = ast.result

    assert op.python_func_str == 'lambda x,y,z: (x+(y+(5.0+z)))'

def test_min_tokens_decorator():
    with pytest.raises(parse.ParseException):
        parse.min_tokens(3)(lambda f: None)([1,2])

    parse.min_tokens(3)(lambda f: None)([1,2,3])

def test_parse_subscript_var():
    tokens = lex.lex('x_{1}')
    ast = parse.parse_var_subscript(tokens)
    var = ast.result

    assert isinstance(var, parse.ASTVar)
    assert var.name == 'x1'

def test_parse_superscript_var():
    tokens = lex.lex('x_{2}')
    ast = parse.parse_var_superscript(tokens)
    op = ast.result

    assert isinstance(op, parse.ASTBinaryOp)
    assert op.python_func(3) == 9

def test_consume_scope():
    tokens = lex.lex('\\frac{1}{2}')
    scoped_tokens = parse.consume_scope(tokens[1:], start=lex.LexToken.Type.COMMAND_ARG_START, end=lex.LexToken.Type.COMMAND_ARG_END)

    assert len(scoped_tokens.result) == 1
    assert len(scoped_tokens.remainder) == 3

def test_parse_binary_op():
    tokens = lex.lex('\\frac{1}{2}+1')
    ast = parse.parse_binary_op(tokens)
    op = ast.result

    assert isinstance(op, parse.ASTBinaryOp)
    assert isinstance(op.left_arg, parse.ASTArg)
    assert isinstance(op.right_arg, parse.ASTArg)
    assert op.left_arg.value == '1'
    assert op.right_arg.value == '2'
    assert len(ast.remainder) == 2

def test_parse_expression():
    tokens = lex.lex('(1+2+3)')
    ast = parse.parse_expression(tokens)
    expr = ast.result

    assert isinstance(expr, parse.ASTExpression)

# TODO: pytest parameterize
def test_parse():
    tokens = lex.lex('(1+2+3)')
    ast = parse.parse(tokens)
    expr = ast.result

    assert isinstance(expr, parse.ASTExpression)