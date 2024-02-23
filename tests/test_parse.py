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