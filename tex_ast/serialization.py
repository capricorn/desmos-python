from typing import Any
from json import JSONEncoder

class ASTExpressionEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return { 'type': 'ASTExpression', 'children': []}