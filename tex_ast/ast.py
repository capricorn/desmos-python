from dataclasses import dataclass
from typing import List, Self, Optional
from enum import Enum, auto

from parse import lex

class PythonRepresentable():
    @property
    def python(self) -> str:
        return ''

class DictRepresentable():
    # TODO: ABC?
    @property
    def dict(self) -> dict:
        return {}

@dataclass
class ASTNode(PythonRepresentable, DictRepresentable):
    children: List[Self]

@dataclass
class ASTExpression(ASTNode):
    @property
    def dict(self) -> dict:
        # TODO: Iterate children
        return { 'type': 'ASTExpression', 'children': []}

    @property
    def python(self) -> str:
        return f'({self.children[0].python})'

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
    def dict(self) -> dict:
        return {
            'type': 'ASTBinaryOp',
            'op': str(self.type),
            'left_arg': self.left_arg.dict,
            'right_arg': self.right_arg.dict
        }

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
    def dict(self) -> dict:
        return { 'type': 'ASTVar', 'name': self.name }

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
    def dict(self) -> dict:
        return { 'type': 'ASTNumber', 'number': str(self.number) }

    @property
    def python(self) -> str:
        return str(self.number)

@dataclass
class ASTParen(ASTNode):
    ...

@dataclass
class ASTUnaryCommand(ASTNode):
    class Type(Enum):
        SQRT = auto()
        NEGATIVE = auto()

        @staticmethod 
        def from_token(funcToken: lex.LexToken.Type) -> Optional[Self]:
            match funcToken.value:
                case '\\sqrt':
                    return ASTUnaryCommand.Type.SQRT
                case '-':
                    return ASTUnaryCommand.Type.NEGATIVE
            
            return None

    type: Type
    arg: ASTNode

    @property
    def dict(self) -> dict:
        # TODO
        raise NotImplementedError()
    
    @property
    def python(self) -> str:
        # TODO
        raise NotImplementedError()