from dataclasses import dataclass
from typing import List, Self, Optional, Set
from enum import Enum, auto

from parse import lex

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

        @staticmethod 
        def from_token(funcToken: lex.LexToken.Type) -> Optional[Self]:
            match funcToken.value:
                case '+':
                    return ASTBinaryOp.Type.ADD
                case '\\cdot':
                    return ASTBinaryOp.Type.MULTIPLY
            
            return None
        
        def __str__(self) -> str:
            match self:
                case ASTBinaryOp.Type.ADD:
                    return '+'
                case ASTBinaryOp.Type.MULTIPLY:
                    return '*'
        
    type: Type
    left_arg: ASTNode
    right_arg: ASTNode

    @property
    def python(self) -> str:
        return f'({self.left_arg.python}{str(self.type)}{self.right_arg.python})'

    @property
    def python_func(self) -> str:
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
            results.extend(self.right_arg.vars())
        
        return results

@dataclass
class ASTVar(ASTNode):
    name: str

    @property
    def python(self) -> str:
        return self.name

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