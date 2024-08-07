from typing import List, Dict, Type as TypingType
from stella_types import Program, DeclFun, Param, Expr, Var, Succ, ConstBool, ConstInt, If, Type, TypeNat, TypeBool, TypeFun, TypeRecord, NatIsZero, Abstraction
from context import Context, Errors


def generate_empty_context() -> Context:
    return Context()


TYPE_NAT = TypeNat()
TYPE_BOOL = TypeBool()


def typecheck_program(ast: Program):
    ctx = generate_empty_context()
    for decl in ast.declarations:
        if isinstance(decl, DeclFun):
            typecheck_function_decl(decl, ctx)
            ctx.symbol_table[decl.name] = TypeFun([param.param_type for param in decl.parameters], decl.return_type)
            if decl.name == 'main':
                ctx.has_main = True
        else:
            raise Exception('Unknown declaration type')
    if not ctx.has_main:
        raise Exception(Errors.MISSING_MAIN)
    print('Everything typechecks!')


def typecheck_function_decl(decl: DeclFun, ctx: Context):
    param = decl.parameters[0]
    symbols_copy = ctx.symbol_table.copy()
    symbols_copy[param.name] = param.param_type
    ctx_copy = Context()
    ctx_copy.symbol_table = symbols_copy

    body_type = typecheck_expr(decl.return_value, ctx_copy)
    verify_types_match(decl.return_type, body_type)


def typecheck_expr(expr: Expr, ctx: Context) -> Type:
    if isinstance(expr, Var):
        if expr.name not in ctx.symbol_table:
            raise Exception(Errors.UNDEFINED_VARIABLE)
        return ctx.symbol_table[expr.name]
    elif isinstance(expr, Succ):
        expr_type = typecheck_expr(expr.expr, ctx)
        verify_types_match(TYPE_NAT, expr_type)
        return TYPE_NAT
    elif isinstance(expr, ConstBool):
        return TYPE_BOOL
    elif isinstance(expr, ConstInt):
        return TYPE_NAT
    elif isinstance(expr, If):
        cond_type = typecheck_expr(expr.condition, ctx)
        verify_types_match(TYPE_BOOL, cond_type)
        then_type = typecheck_expr(expr.then_expr, ctx)
        else_type = typecheck_expr(expr.else_expr, ctx)
        verify_types_match(then_type, else_type)
        return then_type
    else:
        raise Exception('Unknown expression type ' + expr.__class__.__name__)


def verify_types_match(expected: Type, actual: Type):
    if isinstance(expected, TypeFun) and not isinstance(actual, TypeFun):
        raise Exception(Errors.NOT_A_FUNCTION)
    if not isinstance(expected, TypeFun) and isinstance(actual, TypeFun):
        raise Exception(Errors.UNEXPECTED_LAMBDA)
    if type(expected) == type(actual):
        if isinstance(expected, TypeFun) and isinstance(actual, TypeFun):
            try:
                verify_types_match(expected.parameters_types[0], actual.parameters_types[0])
            except:
                raise Exception(Errors.UNEXPECTED_TYPE_FOR_PARAMETER)
            verify_types_match(expected.return_type, actual.return_type)
    else:
        raise Exception(Errors.UNEXPECTED_TYPE_FOR_EXPRESSION)
