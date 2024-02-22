from dataclasses import dataclass
from enum import Enum, auto
from typing import List

@dataclass
class LexToken:
    class Type(Enum):
        COMMAND = auto()
        COMMAND_ARG_START = auto()
        COMMAND_ARG_END = auto()
        NUMBER = auto()
    
    type: Type
    value: str
    # Start index in input string, inclusive.
    start_idx: int
    # End index in input string, inclusive. 
    end_idx: int

class LexState(Enum):
    NONE = auto()
    COMMAND = auto()
    NUMBER = auto()

def lex(input: str) -> List[LexToken]:
    state = LexState.NONE
    token_start = 0
    tokens = []

    i = 0
    while i < len(input):
        ch = input[i]
        match state:
            case LexState.COMMAND:
                if ch == '\\' or ch == ' ' or ch == '{':
                    tokens.append(LexToken(
                        type=LexToken.Type.COMMAND,
                        value=input[token_start:i],
                        start_idx=token_start,
                        end_idx=i
                    ))
                    state = LexState.NONE
                    continue
            case LexState.NUMBER:
                if ch.isdigit() or ch == '.':
                    break
                else:
                    # TODO: Raise lex error if multiple decimals occur
                    tokens.append(LexToken(
                        type=LexToken.Type.NUMBER,
                        value=input[token_start:i],
                        start_idx=token_start,
                        end_idx=i
                    ))
                    # TODO: Find a way to avoid repeating state.. maybe lookahead is better?
                    state = LexState.NONE
                    continue
            case LexState.NONE:
                if ch == '\\':
                    state = LexState.COMMAND
                    token_start = i
                elif ch.isdigit():
                    state = LexState.NUMBER
                    token_start = i
                elif ch == '{':
                    tokens.append(LexToken(
                        type=LexToken.Type.COMMAND_ARG_START,
                        value=ch,
                        start_idx=i,
                        end_idx=i
                    ))
                elif ch == '}':
                    tokens.append(LexToken(
                        type=LexToken.Type.COMMAND_ARG_END,
                        value=ch,
                        start_idx=i,
                        end_idx=i
                    ))
            
        i += 1
    
    if token_start < len(input):
        token_type = None
        match state:
            case LexState.COMMAND:
                token_type = LexToken.Type.COMMAND
            case LexState.NUMBER:
                token_type = LexToken.Type.NUMBER

        if token_type:
            tokens.append(LexToken(
                type=token_type,
                value=input[token_start:],
                start_idx=token_start,
                end_idx=i
            ))
    
    return tokens