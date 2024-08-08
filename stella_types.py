from typing import List, Union

class Type:
    pass

class TypeBool(Type):
    pass

class TypeNat(Type):
    pass

class TypeFun(Type):
    def __init__(self, parameters_types: List[Type], return_type: Type):
        self.parameters_types = parameters_types
        self.return_type = return_type

class Expr:
    pass

class Var(Expr):
    def __init__(self, name: str):
        self.name = name

class Succ(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

class ConstBool(Expr):
    pass

class ConstInt(Expr):
    pass

class If(Expr):
    def __init__(self, condition: Expr, then_expr: Expr, else_expr: Expr):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

class NatIsZero(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

class NatRec(Expr):
    def __init__(self, n: Expr, initial: Expr, step: Expr):
        self.n = n
        self.initial = initial
        self.step = step

class Abstraction(Expr):
    def __init__(self, parameters: List['Parameter'], return_value: Expr):
        self.parameters = parameters
        self.return_value = return_value

class Application(Expr):
    def __init__(self, function: Expr, arguments: List[Expr]):
        self.function = function
        self.arguments = arguments

class Parameter:
    def __init__(self, name: str, param_type: Type):
        self.name = name
        self.param_type = param_type

class DeclFun:
    def __init__(self, name: str, parameters: List[Parameter], return_value: Expr, return_type: Type):
        self.name = name
        self.parameters = parameters
        self.return_value = return_value
        self.return_type = return_type

class Program:
    def __init__(self, declarations: List[DeclFun]):
        self.declarations = declarations
