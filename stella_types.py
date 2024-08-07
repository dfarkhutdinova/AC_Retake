from typing import Any, Dict, List, Union


class Type:
    pass


class TypeNat(Type):
    def __init__(self):
        self.type = 'TypeNat'


class TypeBool(Type):
    def __init__(self):
        self.type = 'TypeBool'


class TypeFun(Type):
    def __init__(self, parameters_types: List[Type], return_type: Type):
        self.parameters_types = parameters_types
        self.return_type = return_type


class TypeRecord(Type):
    def __init__(self, fields: Dict[str, Type]):
        self.type = 'TypeRecord'
        self.fields = fields


class Param:
    def __init__(self, name: str, param_type: Type):
        self.name = name
        self.param_type = param_type


class Expr:
    pass


class Var(Expr):
    def __init__(self, name: str):
        self.name = name


class Succ(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr


class ConstBool(Expr):
    def __init__(self, value: bool):
        self.value = value


class ConstInt(Expr):
    def __init__(self, value: int):
        self.value = value


class If(Expr):
    def __init__(self, condition: Expr, then_expr: Expr, else_expr: Expr):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr


class NatIsZero(Expr):
    def __init__(self, expr: Expr):
        self.type = 'NatIsZero'
        self.expr = expr


class NatRec(Expr):
    def __init__(self, n: Expr, initial: Expr, step: Expr):
        self.type = 'NatRec'
        self.n = n
        self.initial = initial
        self.step = step



class Abstraction(Expr):
    def __init__(self, parameters: List['Param'], return_value: Expr):
        self.type = 'Abstraction'
        self.parameters = parameters
        self.return_value = return_value



class DeclFun:
    def __init__(self, name: str, parameters: List[Param], return_type: Type, return_value: Expr):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.return_value = return_value


class Program:
    def __init__(self, declarations: List[DeclFun]):
        self.declarations = declarations
