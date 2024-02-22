from parse import parse
from parse import lex

def test_parse_number():
    tokens = lex.lex('5\cdot 3')
    number = parse.parse_number(tokens)

    assert len(number.remainder) == len(tokens)-1
    assert isinstance(number.result, parse.ASTNumber)
    assert number.result.number == 5