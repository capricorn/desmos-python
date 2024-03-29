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

def test_var_lex():
    input = 'x\\cdot\\sqrt{2}'
    tokens = lex.lex(input)

    assert tokens[0].value == 'x'

def test_arithmetic_op_lex():
    input = 'x+3-y+2'
    tokens = lex.lex(input)

    assert len(tokens) == 7
    assert tokens[0].type == lex.LexToken.Type.VAR
    assert tokens[1].type == lex.LexToken.Type.COMMAND
    assert tokens[2].type == lex.LexToken.Type.NUMBER
    assert tokens[3].type == lex.LexToken.Type.COMMAND
    assert tokens[4].type == lex.LexToken.Type.VAR
    assert tokens[5].type == lex.LexToken.Type.COMMAND
    assert tokens[6].type == lex.LexToken.Type.NUMBER

def test_subscript_lex():
    input = 'x_{1}+3'
    tokens = lex.lex(input)

    assert tokens[1].type == lex.LexToken.Type.SUBSCRIPT

def test_arg_lex():
    input = 'x_{1}+\frac{1}{2}'
    tokens = lex.lex(input)

    #assert tokens
    args = [ arg for arg in tokens if arg.type == lex.LexToken.Type.ARG ]
    assert len(args) == 3

    arg_values = [ arg.value for arg in args ]
    assert arg_values == ['1', '1', '2']

def test_paren_lex():
    input = '()'
    tokens = lex.lex(input)
    token_types = list(map(lambda t: t.type, tokens))

    assert token_types == [ lex.LexToken.Type.PAREN_LEFT, lex.LexToken.Type.PAREN_RIGHT ]