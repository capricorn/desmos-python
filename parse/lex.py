from dataclasses import dataclass
from enum import Enum, auto
from typing import List

@dataclass
class LexToken:
    class Type(Enum):
        COMMAND = auto()
        COMMAND_ARG_START = auto()
        COMMAND_ARG_END = auto()
    
    type: Type
    value: str
    # Start index in input string, inclusive.
    start_idx: int
    # End index in input string, inclusive. 
    end_idx: int

class LexState(Enum):
    NONE = auto()
    COMMAND = auto()

def lex(input: str) -> List[LexToken]:
    state = LexState.NONE
    token_start = 0
    tokens = []

    for i in range(0, len(input)):
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
                    if ch == ' ':
                        state = LexState.NONE
                    if ch == '{':
                        tokens.append(LexToken(
                            type=LexToken.Type.COMMAND_ARG_START,
                            value=ch,
                            start_idx=i,
                            end_idx=i
                        ))
                        state = LexState.NONE

            case LexState.NONE:
                if ch == '\\':
                    state = LexState.COMMAND
                    token_start = i
                elif ch == '}':
                    tokens.append(LexToken(
                        type=LexToken.Type.COMMAND_ARG_END,
                        value=ch,
                        start_idx=i,
                        end_idx=i
                    ))
    
    if state == LexState.COMMAND and token_start < len(input):
        tokens.append(LexToken(
            type=LexToken.Type.COMMAND,
            value=input[token_start:],
            start_idx=token_start,
            end_idx=i
        ))
    
    return tokens