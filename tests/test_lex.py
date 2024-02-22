from parse import lex

def test_noarg_command_lex():
    input = '\\sqrt 2\\cdot 3'
    tokens = lex.lex(input)

    token_values = list(map(lambda f: f.value, tokens))

    assert '\\sqrt' in token_values
    assert '\\cdot' in token_values

def test_arg_command_lex():
    '''Test a command with an associated argument in curly braces'''

    input = '\\sqrt{2}'
    tokens = lex.lex(input)

    assert tokens[1].type == lex.LexToken.Type.COMMAND_ARG_START
    assert tokens[-1].type == lex.LexToken.Type.COMMAND_ARG_END

def test_number_lex():
    input = '\\sqrt{2}\\cdot 3.2'
    tokens = lex.lex(input)

    numbers = list(map(lambda f: f.value, tokens))

    assert len(tokens) == 6
    assert '2' in numbers
    assert '3.2' in numbers
