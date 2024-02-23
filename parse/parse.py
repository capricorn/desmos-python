from dataclasses import dataclass
from typing import List, Self

from parse import lex

@dataclass
class ASTNode:
    children: List[Self]

@dataclass
class ASTVar(ASTNode):
    name: str

@dataclass
class ASTNumber(ASTNode):
    number: float

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