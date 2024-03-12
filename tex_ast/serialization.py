from typing import Any
from json import JSONEncoder

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