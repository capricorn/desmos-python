from typing import Any
from json import JSONEncoder

class ASTExpressionEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return { 'type': 'ASTExpression', 'children': []}
    

class ASTVarEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return { 'type': 'ASTVar', 'name': o.name }

class ASTNumberEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return { 'type': 'ASTNumber', 'number': str(o.number) }