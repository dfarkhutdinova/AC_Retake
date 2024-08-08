from typing import Dict, Optional, List


class Context:
    def __init__(self):
        self.variables: Dict[str, 'Value'] = {}
        self.functions: Dict[str, 'FunctionDef'] = {}

    def add_variable(self, name: str, value: 'Value'):
        if name in self.variables:
            raise ValueError(f"Variable '{name}' is already defined")
        self.variables[name] = value

    def get_variable(self, name: str) -> 'Value':
        if name not in self.variables:
            raise ValueError(f"Variable '{name}' is not defined")
        return self.variables[name]

    def add_function(self, name: str, function: 'FunctionDef'):
        if name in self.functions:
            raise ValueError(f"Function '{name}' is already defined")
        self.functions[name] = function

    def get_function(self, name: str) -> 'FunctionDef':
        if name not in self.functions:
            raise ValueError(f"Function '{name}' is not defined")
        return self.functions[name]


class Value:
    def __init__(self, value: Optional[int] = None):
        self.value = value


class FunctionDef:
    def __init__(self, name: str, params: List[str], body: 'Expr'):
        self.name = name
        self.params = params
        self.body = body

