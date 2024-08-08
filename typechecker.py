from stella_types import *
from typing import Dict


class Context:
    def __init__(self):
        self.symbol_table: Dict[str, Type] = {}
        self.has_main: bool = False


class Errors:
    UNEXPECTED_TYPE_FOR_PARAMETER = 'ERROR_UNEXPECTED_TYPE_FOR_PARAMETER'
    UNEXPECTED_TYPE_FOR_EXPRESSION = 'ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION'
    UNEXPECTED_LAMBDA = 'ERROR_UNEXPECTED_LAMBDA'
    NOT_A_FUNCTION = 'ERROR_NOT_A_FUNCTION'
    UNDEFINED_VARIABLE = 'ERROR_UNDEFINED_VARIABLE'
    MISSING_MAIN = 'ERROR_MISSING_MAIN'


TYPE_NAT = TypeNat()
TYPE_BOOL = TypeBool()


def generate_empty_context() -> Context:
    return Context()


def typecheck_program(ast: Program):
    ctx = generate_empty_context()
    for decl in ast.declarations:
        if isinstance(decl, DeclFun):
            typecheck_function_decl(decl, ctx)
            ctx.symbol_table[decl.name] = TypeFun(
                [decl.parameters[0].param_type],
                decl.return_type
            )
            if decl.name == 'main':
                ctx.has_main = True
        else:
            raise ValueError('Unknown declaration type')

    if not ctx.has_main:
        raise ValueError(Errors.MISSING_MAIN)

    print('Everything typechecks!')


def typecheck_function_decl(decl: DeclFun, ctx: Context):
    name, parameters, return_value, return_type = decl.name, decl.parameters, decl.return_value, decl.return_type
    param = parameters[0]
    symbols_copy = ctx.symbol_table.copy()
    symbols_copy[param.name] = param.param_type
    ctx_copy = Context()
    ctx_copy.symbol_table = symbols_copy
    ctx_copy.has_main = ctx.has_main

    body_type = typecheck_expr(return_value, ctx_copy)
    verify_types_match(return_type, body_type)


def typecheck_expr(expr: Expr, ctx: Context) -> Type:
    if isinstance(expr, Var):
        if expr.name not in ctx.symbol_table:
            raise ValueError(Errors.UNDEFINED_VARIABLE)
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

    elif isinstance(expr, NatIsZero):
        expr_type = typecheck_expr(expr.expr, ctx)
        verify_types_match(TYPE_NAT, expr_type)
        return TYPE_BOOL

    elif isinstance(expr, NatRec):
        n_type = typecheck_expr(expr.n, ctx)
        verify_types_match(TYPE_NAT, n_type)
        initial_type = typecheck_expr(expr.initial, ctx)
        step_expected_type = TypeFun(
            [TYPE_NAT],
            TypeFun([initial_type], initial_type)
        )
        step_actual_type = typecheck_expr(expr.step, ctx)
        verify_types_match(step_expected_type, step_actual_type)
        return initial_type

    elif isinstance(expr, Abstraction):
        param = expr.parameters[0]
        symbols_copy = ctx.symbol_table.copy()
        symbols_copy[param.name] = param.param_type
        ctx_copy = Context()
        ctx_copy.symbol_table = symbols_copy
        ctx_copy.has_main = ctx.has_main

        body_type = typecheck_expr(expr.return_value, ctx_copy)
        return TypeFun([param.param_type], body_type)

    elif isinstance(expr, Application):
        func_type = typecheck_expr(expr.function, ctx)
        if not isinstance(func_type, TypeFun):
            raise ValueError(Errors.NOT_A_FUNCTION)
        arg = expr.arguments[0]
        arg_type = typecheck_expr(arg, ctx)
        param_type = func_type.parameters_types[0]
        verify_types_match(param_type, arg_type)
        return func_type.return_type

    else:
        raise ValueError('Unknown expression type ' + str(type(expr)))


def verify_types_match(expected: Type, actual: Type):
    if isinstance(expected, TypeFun) and not isinstance(actual, TypeFun):
        raise ValueError(Errors.NOT_A_FUNCTION)
    if not isinstance(expected, TypeFun) and isinstance(actual, TypeFun):
        raise ValueError(Errors.UNEXPECTED_LAMBDA)
    if type(expected) == type(actual):
        if isinstance(expected, TypeFun) and isinstance(actual, TypeFun):
            try:
                verify_types_match(expected.parameters_types[0], actual.parameters_types[0])
            except:
                raise ValueError(Errors.UNEXPECTED_TYPE_FOR_PARAMETER)
            verify_types_match(expected.return_type, actual.return_type)
    else:
        raise ValueError(Errors.UNEXPECTED_TYPE_FOR_EXPRESSION)
