from dataclasses import dataclass
from typing import Any, List, Self, Optional, Callable
from enum import Enum, auto
from json import JSONEncoder

from parse import lex
from tex_ast.ast import *

def min_tokens(min_tokens: int):
    def wrapper(f: Callable[[List[lex.LexToken]], ParseResult]):
        def handle_tokens(tokens: List[lex.LexToken]) -> ParseResult:
            if len(tokens) < min_tokens:
                raise ParseException(f'Token list of insufficient length: {len(tokens)} < {min_tokens}')

            return f(tokens)
        
        return handle_tokens
    
    return wrapper

@dataclass
class ParseResult:
    result: ASTNode
    remainder: List[lex.LexToken]

@dataclass 
class ScopeResult:
    result: List[lex.LexToken]
    remainder: List[lex.LexToken]

class ParseException(Exception):
    ...

def parse_number(tokens: List[lex.LexToken]) -> ParseResult:
    if len(tokens) < 1:
        raise ParseException('Empty token list.')
    
    if tokens[0].type == lex.LexToken.Type.NUMBER:
        return ParseResult(
            ASTNumber(children=[], number=float(tokens[0].value)), 
            tokens[1:])
    
    raise ParseException(f'Failed to parse token as number: {tokens[0].value}')

def parse_variable(tokens: List[lex.LexToken]) -> ParseResult:
    if len(tokens) < 1:
        raise ParseException('Empty token list.')
    
    if tokens[0].type == lex.LexToken.Type.VAR:
        return ParseResult(
            ASTVar(children=[], name=tokens[0].value),
            tokens[1:])

    raise ParseException(f'Failed to parse token as variable: {tokens[0].value}')

def parse_infix_binary_op_left_arg(tokens: List[lex.LexToken]) -> ParseResult:
    try:
        return parse_number(tokens).result
    except:
        ...
    
    return parse_variable(tokens).result

def parse_infix_binary_op_right_arg(tokens: List[lex.LexToken]) -> ParseResult:
    try:
        return parse_infix_binary_op(tokens).result
    except:
        ...
    
    try:
        return parse_number(tokens).result
    except:
        ...

    return parse_variable(tokens).result

def parse_infix_binary_op(tokens: List[lex.LexToken]) -> ParseResult:
    ''' Parse operators of the form `a OP b`.

    This differs from typical latex functions such as `\\frac{a}{b}` which pass
    the args directly after.
    '''

    if len(tokens) < 3:
        raise ParseException(f'Token list of insufficient length: {len(tokens)}')
    
    left_arg, function, right_arg = tokens[:3]
    function_type = ASTBinaryOp.Type.from_token(function)

    if function_type is None:
        raise ParseException(f'Failed to extract function type: {function.value}')

    left_arg = parse_infix_binary_op_left_arg(tokens)
    # Currently no paren support
    right_arg = parse_infix_binary_op_right_arg(tokens[2:])

    return ParseResult(
        ASTBinaryOp(children=[], type=function_type, left_arg=left_arg, right_arg=right_arg),
        tokens[3:]
    )

@min_tokens(5)
def parse_var_subscript(tokens: List[lex.LexToken]) -> ParseResult:
    # ex: x_{33}; 5 tokens -- [VAR, SUBSCRIPT, OPEN ARG CLOSE ]

    var,_,_,arg,_ = tokens[:5]
    name = var.value + arg.value

    return ParseResult(
        ASTVar(children=[], name=name),
        tokens[5:]
    )

@min_tokens(1)
def parse_arg(tokens: List[lex.LexToken]) -> ParseResult:
    return ParseResult(
        ASTArg(children=[], value=tokens[0].value),
        tokens[1:]
    )

@min_tokens(5)
def parse_var_superscript(tokens: List[lex.LexToken]) -> ParseResult:
    var,_,_,arg = tokens[:4]

    var = parse_variable(tokens).result

    if arg.type == lex.LexToken.Type.ARG:
        arg = parse_arg(tokens[3:]).result
        remaining = tokens[5:]
    else:
        # TODO: Parse expression between tokens
        raise NotImplementedError()

    return ParseResult(
        ASTBinaryOp(children=[], type=ASTBinaryOp.Type.POW, left_arg=var, right_arg=arg),
        remaining
    )

# TODO: Return scope + remaining tokens (past scope)
def consume_scope(
    tokens: List[lex.LexToken], 
    start: lex.LexToken.Type, 
    end: lex.LexToken.Type
) -> ScopeResult:
    scoped_tokens = []
    scope = 0
    for i, token in enumerate(tokens):
        if token.type == start:
            scope += 1
            continue
        elif token.type == end:
            assert scope >= 0
            scope -= 1
        
        if scope == 0:
            i += 1
            break
        else:
            scoped_tokens.append(token)
        
    return ScopeResult(
        result=scoped_tokens,
        remainder=tokens[i:]
    )

def parse_binary_op(tokens: List[lex.LexToken]) -> ParseResult:
    first_arg_scope = consume_scope(
        tokens[1:],
        start=lex.LexToken.Type.COMMAND_ARG_START,
        end=lex.LexToken.Type.COMMAND_ARG_END)
    first_arg = first_arg_scope.result

    second_arg_scope = consume_scope(
        first_arg_scope.remainder,
        start=lex.LexToken.Type.COMMAND_ARG_START,
        end=lex.LexToken.Type.COMMAND_ARG_END)
    second_arg = second_arg_scope.result

    first_arg = parse_arg(first_arg).result
    second_arg = parse_arg(second_arg).result

    return ParseResult(
        ASTBinaryOp(
            children=[], 
            type=ASTBinaryOp.Type.from_token(tokens[0]), 
            left_arg=first_arg, 
            right_arg=second_arg),
        remainder=second_arg_scope.remainder)
    
@min_tokens(2)
def parse_expression(tokens: List[lex.LexToken]) -> ParseResult:
    scope_tokens = consume_scope(
        tokens=tokens,
        start=lex.LexToken.Type.PAREN_LEFT,
        end=lex.LexToken.Type.PAREN_RIGHT
    ) 

    expr = parse(scope_tokens.result)

    return ParseResult(
        ASTExpression(children=[expr.result]),
        remainder=scope_tokens.remainder
    )

def consume_while(tokens: List[lex.LexToken], pred: Callable[[lex.LexToken], bool]) -> ScopeResult:
    for i in range(len(tokens)):
        if not pred(tokens[i]):
            break
    
    return ScopeResult(tokens[:i+1], tokens[i:])

def parse_implicit_multiplication(tokens: List[lex.LexToken]) -> ParseResult:
    ''' Parse a sequence of the form (Var|Number)+; ex: 2xt 
    
    This should produce a tree of the form 2*(x*t)
    '''

    # Simple: consume the sequence as long as (Number|Var) is satisfied
    # One issue: the final var needs to _not_ have a trailing command applied
    # TODO: Implement `consume_while` predicate
    #is_implicit = lambda token: 
    def is_implicit(token: lex.LexToken) -> bool:
        # TODO: Check that following token is not a postfix command
        # In that case, may need to pass more state (pos, tokens, ...) 
        return (token.type == lex.LexToken.Type.VAR) or (token.type == lex.LexToken.Type.NUMBER)
    
    consume_result = consume_while(tokens, is_implicit)
    print(f'consume result: {consume_result.result}')

    def token_node(token: lex.LexToken) -> Optional[ASTNode]:
        match token.type:
            case lex.LexToken.Type.NUMBER:
                return ASTNumber(children=[], number=token.value)
            case lex.LexToken.Type.VAR:
                return ASTVar(children=[], name=token.value)
        
        return None

    # TODO: Generic approach to building n-ary trees?
    # TODO: Worth testing tree building elsewhere..?
    def build_tree(tokens: List[lex.LexToken]) -> ASTBinaryOp:
        assert len(tokens) > 1
        node = ASTBinaryOp(
            children=[],
            type=ASTBinaryOp.Type.MULTIPLY,
            left_arg=None,
            right_arg=None)

        node.left_arg = token_node(tokens[0])#ASTNode(tokens[0])   # TODO: Process as node
        node.right_arg = build_tree_rec(tokens[1:], node)
        return node

    def build_tree_rec(tokens: List[lex.LexToken], parent: ASTBinaryOp) -> ASTNode:
        print(f'tokens: {tokens}')
        if len(tokens) > 1:
            node = ASTBinaryOp(
                children=[], 
                type=ASTBinaryOp.Type.MULTIPLY, 
                left_arg=None, 
                right_arg=None)

            print('building sub op')
            # TODO: Obtain proper node type (should be VAR/NUMBER)
            node.left_arg = token_node(tokens[0])#ASTNode(tokens[0])
            node.right_arg = build_tree_rec(tokens[1:], node)
            return node
        else:
            # TODO: Obtain node from lexical token
            return token_node(tokens[0])#ASTNode(children=[tokens[0]])


    ast = build_tree(consume_result.result)
    # TODO: Join tokens to binary op tree
    # Probably best to join recursively? (A reduce could work..?)

    return ParseResult(
        result=ast,
        remainder=consume_result.remainder
    )

# Think: prefix op
def parse_unary_op(tokens: List[lex.LexToken]) -> ParseResult:
    ...

def parse(tokens: List[lex.LexToken]) -> ParseResult:
    # At the top-level the possibilities (currently) are:
    # - Expression
    # - Binary op
    # TODO: Unary, function assignment
    # TODO: 'Flat' binary op (using parens)
    try:
        return parse_expression(tokens)
    except:
        ...
    
    try:
        return parse_binary_op(tokens)
    except:
        ... 

    try:
        return parse_infix_binary_op(tokens)
    except:
        ...
    
    raise ParseException('Failed to parse tokens.')

def parse_program(tex: str) -> ASTNode:
    tokens = lex.lex(tex)
    return parse(tokens).result