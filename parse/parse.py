from dataclasses import dataclass
from typing import List, Self, Optional, Callable
from enum import Enum, auto

from parse import lex

def min_tokens(min_tokens: int):
    def wrapper(f: Callable[[List[lex.LexToken]], ParseResult]):
        def handle_tokens(tokens: List[lex.LexToken]) -> ParseResult:
            if len(tokens) < min_tokens:
                raise ParseException(f'Token list of insufficient length: {len(tokens)} < {min_tokens}')

            return f(tokens)
        
        return handle_tokens
    
    return wrapper

class PythonRepresentable():
    @property
    def python(self) -> str:
        return ''

@dataclass
class ASTNode(PythonRepresentable):
    children: List[Self]

@dataclass 
class ASTBinaryOp(ASTNode):
    class Type(Enum):
        ADD = auto() 
        MULTIPLY = auto()
        POW = auto()
        DIVIDE = auto()

        @staticmethod 
        def from_token(funcToken: lex.LexToken.Type) -> Optional[Self]:
            match funcToken.value:
                case '+':
                    return ASTBinaryOp.Type.ADD
                case '\\cdot':
                    return ASTBinaryOp.Type.MULTIPLY
                case '\\frac':
                    return ASTBinaryOp.Type.DIVIDE
            
            return None
        
        def __str__(self) -> str:
            match self:
                case ASTBinaryOp.Type.ADD:
                    return '+'
                case ASTBinaryOp.Type.MULTIPLY:
                    return '*'
                case ASTBinaryOp.Type.POW:
                    return '**'
                case ASTBinaryOp.Type.DIVIDE:
                    return '/'
        
    type: Type
    left_arg: ASTNode
    right_arg: ASTNode

    @property
    def python_func(self):
        return eval(self.python_func_str)

    @property
    def python(self) -> str:
        return f'({self.left_arg.python}{str(self.type)}{self.right_arg.python})'

    @property
    def python_func_str(self) -> str:
        # TODO: Walk tree and collect variables 
        args = ','.join(self.vars)
        if not args == '':
            args = ' ' + args
        return f'lambda{args}: {self.python}'

    @property
    def vars(self) -> List[str]:
        results = []
        if isinstance(self.left_arg, ASTVar):
            results.append(self.left_arg.name)

        if isinstance(self.right_arg, ASTVar):
            results.append(self.right_arg.name)
        elif isinstance(self.right_arg, ASTBinaryOp):
            results.extend(self.right_arg.vars)
        
        return results

@dataclass
class ASTVar(ASTNode):
    name: str

    @property
    def python(self) -> str:
        return self.name

@dataclass
class ASTArg(ASTNode):
    value: str

    @property
    def python(self) -> str:
        return self.value

@dataclass
class ASTNumber(ASTNode):
    number: float

    @property
    def python(self) -> str:
        return str(self.number)

@dataclass
class ASTParen(ASTNode):
    ...

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
def consume_bracket_scope(tokens: List[lex.LexToken]) -> ScopeResult:
    scoped_tokens = []
    scope = 0
    for i, token in enumerate(tokens):
        if token.type == lex.LexToken.Type.COMMAND_ARG_START:
            scope += 1
            continue
        elif token.type == lex.LexToken.Type.COMMAND_ARG_END:
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
    first_arg_scope = consume_bracket_scope(tokens[1:]) 
    first_arg = first_arg_scope.result
    second_arg_scope = consume_bracket_scope(first_arg_scope.remainder)
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