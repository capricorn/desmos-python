from typing import Any
from json import JSONEncoder

from parse import parse

class ASTNodeEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        # TODO -- switch on types; use as top-level encoder
        if isinstance(o, parse.ASTVar):
            return ASTVarEncoder().default(o)
        elif isinstance(o, parse.ASTNumber):
            return ASTNumberEncoder().default(o)
        elif isinstance(o, parse.ASTBinaryOp):
            return ASTBinaryOpEncoder().default(o)

        return super().default(o)

class ASTExpressionEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.dict
    
class ASTVarEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.dict

class ASTNumberEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.dict

class ASTBinaryOpEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.dict