from dataclasses import dataclass
from typing import *
from parse import lex

@dataclass 
class ScopeResult:
    result: List[lex.LexToken]
    remainder: List[lex.LexToken]

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

def consume_while(tokens: List[lex.LexToken], pred: Callable[[lex.LexToken], bool]) -> ScopeResult:
    for i in range(len(tokens)):
        if not pred(tokens[i]):
            break
    
    return ScopeResult(tokens[:i+1], tokens[i:])