import sys
from typing import cast

from antlr4 import FileStream, StdinStream, CommonTokenStream, Token
from stella.stellaParser import stellaParser
from stella.stellaLexer import stellaLexer

ERROR_UNEXPECTED_TYPE_FOR_PARAMETER = "ERROR_UNEXPECTED_TYPE_FOR_PARAMETER"
ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION = "ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION"
ERROR_UNEXPECTED_LAMBDA = "ERROR_UNEXPECTED_LAMBDA"
ERROR_NOT_A_FUNCTION = "ERROR_NOT_A_FUNCTION"
ERROR_UNDEFINED_VARIABLE = "ERROR_UNDEFINED_VARIABLE"
ERROR_MISSING_MAIN = "ERROR_MISSING_MAIN"
ERROR_NOT_A_TUPLE = "ERROR_NOT_A_TUPLE"
ERROR_UNEXPECTED_TUPLE = "ERROR_UNEXPECTED_TUPLE"
ERROR_TUPLE_INDEX_OUT_OF_BOUNDS = "ERROR_TUPLE_INDEX_OUT_OF_BOUNDS"
ERROR_NOT_A_RECORD = "ERROR_NOT_A_RECORD"
ERROR_UNEXPECTED_FIELD_ACCESS = "ERROR_UNEXPECTED_FIELD_ACCESS"
ERROR_UNEXPECTED_RECORD = "ERROR_UNEXPECTED_RECORD"
ERROR_MISSING_RECORD_FIELDS = "ERROR_MISSING_RECORD_FIELDS"
ERROR_UNEXPECTED_RECORD_FIELDS = "ERROR_UNEXPECTED_RECORD_FIELDS"
ERROR_NOT_A_LIST = "ERROR_NOT_A_LIST"
ERROR_AMBIGUOUS_SUM_TYPE = "ERROR_AMBIGUOUS_SUM_TYPE"
ERROR_UNEXPECTED_PATTERN_FOR_TYPE = "ERROR_UNEXPECTED_PATTERN_FOR_TYPE"
ERROR_UNEXPECTED_INJECTION = "ERROR_UNEXPECTED_INJECTION"
ERROR_NONEXHAUSTIVE_MATCH_PATTERNS = "ERROR_NONEXHAUSTIVE_MATCH_PATTERNS"
ERROR_UNEXPECTED_LIST = "ERROR_UNEXPECTED_LIST"
ERROR_AMBIGUOUS_LIST_TYPE = "ERROR_AMBIGUOUS_LIST_TYPE"
ERROR_AMBIGUOUS_VARIANT_TYPE = "ERROR_AMBIGUOUS_VARIANT_TYPE"
ERROR_UNEXPECTED_VARIANT = "ERROR_UNEXPECTED_VARIANT"
ERROR_UNEXPECTED_VARIANT_LABEL = "ERROR_UNEXPECTED_VARIANT_LABEL"
ERROR_EXCEPTION_TYPE_NOT_DECLARED = "ERROR_EXCEPTION_TYPE_NOT_DECLARED"
ERROR_NOT_A_REFERENCE = "ERROR_NOT_A_REFERENCE"
ERROR_AMBIGUOUS_REFERENCE_TYPE = "ERROR_AMBIGUOUS_REFERENCE_TYPE"
ERROR_INCORRECT_NUMBER_OF_ARGUMENTS = "ERROR_INCORRECT_NUMBER_OF_ARGUMENTS"
ERROR_ILLEGAL_EMPTY_MATCHING = "ERROR_ILLEGAL_EMPTY_MATCHING"
ERROR_AMBIGUOUS_PANIC_TYPE = "ERROR_AMBIGUOUS_PANIC_TYPE"
ERROR_AMBIGUOUS_THROW_TYPE = 'ERROR_AMBIGUOUS_THROW_TYPE'


type_env = {}
exception_env = {}


class Type:
    pass


class UnitType(Type):
    def __str__(self):
        return "Unit"

    def __eq__(self, other):
        return isinstance(other, UnitType)


class TupleType(Type):
    def __init__(self, elem_types):
        self.elem_types = elem_types

    def __str__(self):
        return "({})".format(", ".join(str(t) for t in self.elem_types))

    def __eq__(self, other):
        return (isinstance(other, TupleType) and
                self.elem_types == other.elem_types)


class RecordType(Type):
    def __init__(self, fields: dict):
        self.fields = fields

    def __str__(self):
        fields_str = ", ".join(f"{k}: {v}" for k, v in self.fields.items())
        return f"{{{fields_str}}}"

    def __eq__(self, other):
        return (isinstance(other, RecordType) and
                self.fields == other.fields)


class NatType(Type):
    def __str__(self):
        return "Nat"

    def __eq__(self, other):
        return isinstance(other, NatType)


class BoolType(Type):
    def __str__(self):
        return "Bool"

    def __eq__(self, other):
        return isinstance(other, BoolType)


class FunType(Type):
    def __init__(self, param_types, return_type):
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self):
        param_types_str = ", ".join(str(pt) for pt in self.param_types)
        return f"({param_types_str}) -> {self.return_type}"

    def __eq__(self, other):
        return (isinstance(other, FunType) and
                self.param_types == other.param_types and
                self.return_type == other.return_type)


class SumType(Type):
    def __init__(self, left_type, right_type):
        self.left_type = left_type
        self.right_type = right_type

    def __str__(self):
        return f"({self.left_type} + {self.right_type})"

    def __eq__(self, other):
        return isinstance(other, SumType) and self.left_type == other.left_type and self.right_type == other.right_type


class NatRecContext(Type):
    def __init__(self, nat_type, base_case_type, step_function_type):
        self.nat_type = nat_type
        self.base_case_type = base_case_type
        self.step_function_type = step_function_type

    def __str__(self):
        return f"NatRec({self.nat_type}, {self.base_case_type}, {self.step_function_type})"

    def __eq__(self, other):
        return (
            isinstance(other, NatRecContext) and
            self.nat_type == other.nat_type and
            self.base_case_type == other.base_case_type and
            self.step_function_type == other.step_function_type
        )


class ListType(Type):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def __str__(self):
        return f"List[{self.elem_type}]"

    def __eq__(self, other):
        return isinstance(other, ListType) and self.elem_type == other.elem_type


class PatternVar(Type):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"PatternVar({self.name})"

    def __eq__(self, other):
        return isinstance(other, PatternVar) and self.name == other.name


class TypeVariant(Type):
    def __init__(self, fields: dict):
        self.fields = fields

    def __str__(self):
        fields_str = " | ".join(f"{label}: {field_type}" for label, field_type in self.fields.items())
        return f"Variant({fields_str})"

    def __eq__(self, other):
        return isinstance(other, TypeVariant) and self.fields == other.fields


class RefType(Type):
    def __init__(self, ref_type):
        self.ref_type = ref_type

    def __str__(self):
        return f"Ref({self.ref_type})"

    def __eq__(self, other):
        return isinstance(other, RefType) and self.ref_type == other.ref_type


class ExceptionType(Type):
    def __init__(self, exception_name):
        self.exception_name = exception_name

    def __str__(self):
        return f"Exception({self.exception_name})"

    def __eq__(self, other):
        return isinstance(other, ExceptionType) and self.exception_name == other.exception_name


class PanicType(Type):
    def __str__(self):
        return "Panic"

    def __eq__(self, other):
        return isinstance(other, PanicType)


def type_error(msg: str):
    print("TYPE ERROR:", msg, file=sys.stderr)
    sys.exit(1)


def add_standard_functions_to_env():
    type_env['Nat::mul'] = FunType([NatType()], FunType([NatType()], NatType()))
    type_env['Nat::add'] = FunType([NatType()], FunType([NatType()], NatType()))
    type_env['Nat::rec'] = FunType(
        [NatType(), NatType(), FunType([NatType()], FunType([NatType()], NatType()))],
        NatType()
    )


def handle_expr_context(ctx: stellaParser.ExprContext):
    if ctx is None:
        type_error("ERROR: Expression context is None")

    expression_text = ctx.getText() if ctx.getText() is not None else "<unknown expression>"
    print(f"Handling expression: {expression_text}")
    #print(f"Current type environment: {type_env}")
    #print(f"Context type: {type(ctx).__name__}")
    #print_ast(ctx)

    match ctx:
        case stellaParser.ConstTrueContext() | stellaParser.ConstFalseContext():
            return BoolType()

        case stellaParser.ConstIntContext():
            int_value = int(ctx.getText())
            if int_value >= 0:
                return NatType()
            else:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

        case stellaParser.SuccContext():
            expr_type = handle_expr_context(ctx.expr())
            #print(f"Type of expression inside succ: {expr_type}")
            if not isinstance(expr_type, NatType):
                print(f"Type mismatch inside succ: expected 'Nat', got '{expr_type}'")
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return NatType()

        case stellaParser.IsZeroContext():
            expr_type = handle_expr_context(ctx.expr())
            if not isinstance(expr_type, NatType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return BoolType()

        case stellaParser.IfContext():
            condition_type = handle_expr_context(ctx.condition)

            if isinstance(condition_type, PanicType):
                return PanicType()

            if not isinstance(condition_type, BoolType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            then_type = handle_expr_context(ctx.thenExpr)
            else_type = handle_expr_context(ctx.elseExpr)

            if isinstance(then_type, PanicType) and isinstance(else_type, PanicType):
                return PanicType()

            if isinstance(then_type, PanicType):
                return else_type

            if isinstance(else_type, PanicType):
                return then_type

            if then_type != else_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return then_type

        case stellaParser.VarContext():
            name = ctx.name.text
            if name not in type_env:
                type_error(ERROR_AMBIGUOUS_VARIANT_TYPE)
            return type_env[name]

        case stellaParser.ApplicationContext():
            func_type = handle_expr_context(ctx.expr(0))

            if isinstance(func_type, PanicType):
                type_error(ERROR_AMBIGUOUS_PANIC_TYPE)

            if not isinstance(func_type, FunType):
                type_error(ERROR_NOT_A_FUNCTION)

            if len(ctx.expr()) - 1 != len(func_type.param_types):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_PARAMETER)

            if len(ctx.expr()) > 1:
                arg_type = handle_expr_context(ctx.expr(1))

                if isinstance(func_type.param_types[0], SumType):
                    if func_type.param_types[0].left_type is None or func_type.param_types[0].right_type is None:
                        type_error(ERROR_AMBIGUOUS_SUM_TYPE)
                    if not (isinstance(arg_type, SumType) or arg_type == func_type.param_types[0]):
                        type_error(ERROR_UNEXPECTED_TYPE_FOR_PARAMETER)
                elif arg_type != func_type.param_types[0]:
                    type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return func_type.return_type if not isinstance(func_type.return_type, FunType) else func_type.return_type

        case stellaParser.AbstractionContext():
            param_decls = ctx.paramDecl()
            param_types = []

            for param_decl in param_decls:
                param_name = param_decl.name.text
                param_type_ctx = param_decl.stellatype()
                param_type = parse_type(param_type_ctx)

                print(f"Adding parameter '{param_name}' of type '{param_type}' to type environment.")
                type_env[param_name] = param_type
                param_types.append(param_type)

            body_expr = ctx.expr()
            body_type = handle_expr_context(body_expr)
            print(f"Body of lambda returns type '{body_type}'")

            lambda_type = FunType(param_types, body_type)
            return lambda_type

        case stellaParser.TerminatingSemicolonContext():
            expr_type = handle_expr_context(ctx.expr())
            return expr_type

        case stellaParser.ConstUnitContext():
            return UnitType()

        case stellaParser.NatRecContext():
            nat_type = handle_expr_context(ctx.expr(0))
            if not isinstance(nat_type, NatType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            base_case_type = handle_expr_context(ctx.expr(1))

            step_function_type = handle_expr_context(ctx.expr(2))
            if not isinstance(step_function_type, FunType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            if len(step_function_type.param_types) != 1:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_PARAMETER)

            if not isinstance(step_function_type.param_types[0], NatType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_PARAMETER)

            if not isinstance(step_function_type.return_type, FunType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            if (len(step_function_type.return_type.param_types) != 1 or
                    step_function_type.return_type.param_types[0] != base_case_type or
                    step_function_type.return_type.return_type != base_case_type):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return base_case_type

        case stellaParser.TupleContext():
            expr_types = [handle_expr_context(expr) for expr in ctx.expr()]
            return TupleType(expr_types)

        case stellaParser.DotTupleContext():
            tuple_expr_type = handle_expr_context(ctx.expr())
            if not isinstance(tuple_expr_type, TupleType):
                type_error(ERROR_NOT_A_TUPLE)

            index = int(ctx.INTEGER().getText()) - 1
            if index < 0 or index >= len(tuple_expr_type.elem_types):
                type_error(ERROR_TUPLE_INDEX_OUT_OF_BOUNDS)

            return tuple_expr_type.elem_types[index]

        case stellaParser.RecordContext():
            if len(ctx.binding()) == 0:
                return RecordType({})
            field_types = {field.getChild(0).getText(): handle_expr_context(field.getChild(2)) for field in
                           ctx.binding()}
            return RecordType(field_types)

        case stellaParser.DotRecordContext():
            record_type = handle_expr_context(ctx.expr())
            if not isinstance(record_type, RecordType):
                type_error(ERROR_NOT_A_RECORD)

            field_name = ctx.getChild(2).getText()
            #print(f"Accessing field: {field_name}")

            if field_name not in record_type.fields:
                type_error(ERROR_UNEXPECTED_FIELD_ACCESS)

            return record_type.fields[field_name]

        case stellaParser.LetContext():
            for binding in ctx.patternBinding():
                pattern = binding.pattern()
                expr_type = handle_expr_context(binding.expr())

                if pattern.getText() == "{}" and isinstance(expr_type, RecordType) and len(expr_type.fields) == 0:
                    continue

                if isinstance(expr_type, TupleType):
                    elements = pattern.getText().strip("{}").split(",")
                    element_types = []
                    current_type = expr_type

                    while isinstance(current_type, TupleType):
                        element_types.append(current_type.left_type)
                        current_type = current_type.right_type
                    element_types.append(current_type)

                    if len(elements) != len(element_types):
                        type_error(ERROR_UNEXPECTED_TUPLE)

                    for var_name, var_type in zip(elements, element_types):
                        var_name = var_name.strip()
                        type_env[var_name] = var_type
                        #print(f"Binding variable '{var_name}' with type '{var_type}'")

                else:
                    var_name = pattern.getText()
                    type_env[var_name] = expr_type

            in_expr_type = handle_expr_context(ctx.expr())
            return in_expr_type

        case stellaParser.TypeAscContext():
            expr_type = handle_expr_context(ctx.expr())
            ascribed_type = parse_type(ctx.stellatype())
            #print(f"Expression has type '{expr_type}', ascribed type is '{ascribed_type}'")
            if expr_type != ascribed_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return ascribed_type

        case stellaParser.PatternVarContext():
            var_name = ctx.getText()
            if var_name in type_env:
                return type_env[var_name]
            else:
                type_error(ERROR_UNDEFINED_VARIABLE)

        case stellaParser.InlContext():
            expr_type = handle_expr_context(ctx.expr())
            ascribed_type = None
            if isinstance(ctx.parentCtx, stellaParser.TypeAscContext):
                ascribed_type = parse_type(ctx.parentCtx.stellatype())

            if ascribed_type is not None and isinstance(ascribed_type, SumType):
                if ascribed_type.right_type is None:
                    type_error(ERROR_AMBIGUOUS_SUM_TYPE)
                if expr_type != ascribed_type.left_type:
                    type_error(ERROR_UNEXPECTED_INJECTION)
                return SumType(expr_type, ascribed_type.right_type)
            else:
                if expr_type is None:
                    type_error(ERROR_AMBIGUOUS_SUM_TYPE)
                return SumType(expr_type, None)

        case stellaParser.InrContext():
            expr_type = handle_expr_context(ctx.expr())
            ascribed_type = None
            if isinstance(ctx.parentCtx, stellaParser.TypeAscContext):
                ascribed_type = parse_type(ctx.parentCtx.stellatype())

            if ascribed_type is not None and isinstance(ascribed_type, SumType):
                if ascribed_type.left_type is None:
                    type_error(ERROR_AMBIGUOUS_SUM_TYPE)
                if expr_type != ascribed_type.right_type:
                    type_error(ERROR_UNEXPECTED_INJECTION)
                return SumType(ascribed_type.left_type, expr_type)
            else:
                if expr_type is None:
                    type_error(ERROR_AMBIGUOUS_SUM_TYPE)
                return SumType(None, expr_type)

        case stellaParser.MatchContext():
            expr_type = handle_expr_context(ctx.expr())

            match_cases = ctx.matchCase()
            if not match_cases:
                type_error("ERROR_ILLEGAL_EMPTY_MATCHING")

            if len(match_cases) < 2:
                type_error(ERROR_NONEXHAUSTIVE_MATCH_PATTERNS)

            # if len(match_cases) == 0:
            #     type_error(ERROR_ILLEGAL_EMPTY_MATCHING)

            if isinstance(expr_type, SumType):
                inl_case, inr_case = ctx.matchCase()

                if isinstance(inl_case.pattern(), stellaParser.PatternInlContext):
                    var_name_inl = inl_case.pattern().pattern().getText()
                    inl_var_type = expr_type.left_type
                    type_env[var_name_inl] = inl_var_type
                    inl_body_type = handle_expr_context(inl_case.expr())
                else:
                    type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

                if isinstance(inr_case.pattern(), stellaParser.PatternInrContext):
                    var_name_inr = inr_case.pattern().pattern().getText()
                    inr_var_type = expr_type.right_type
                    type_env[var_name_inr] = inr_var_type
                    inr_body_type = handle_expr_context(inr_case.expr())
                else:
                    type_error(ERROR_UNEXPECTED_PATTERN_FOR_TYPE)

                if inl_body_type != inr_body_type:
                    type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

                return inl_body_type

            elif isinstance(expr_type, TypeVariant):
                match_cases = ctx.matchCase()
                common_body_type = None

                for match_case in match_cases:
                    label = match_case.pattern().label.text
                    if label not in expr_type.fields:
                        type_error(ERROR_UNEXPECTED_PATTERN_FOR_TYPE)

                    expected_type = expr_type.fields[label]
                    var_name = match_case.pattern().pattern().getText()
                    type_env[var_name] = expected_type

                    body_type = handle_expr_context(match_case.expr())
                    if common_body_type is None:
                        common_body_type = body_type
                    elif common_body_type != body_type:
                        type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

                return common_body_type

            else:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

        case stellaParser.ListContext():
            if len(ctx.expr()) == 0:
                if hasattr(ctx.parentCtx, 'returnType'):
                    parent_function_type = type_env.get(ctx.parentCtx.name.text)
                    if isinstance(parent_function_type.return_type, ListType):
                        return parent_function_type.return_type

                return ListType(None)

            elem_types = [handle_expr_context(e) for e in ctx.expr()]
            first_elem_type = elem_types[0]
            for t in elem_types:
                if t != first_elem_type:
                    type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return ListType(first_elem_type)

        case stellaParser.ConsListContext():
            head_type = handle_expr_context(ctx.expr(0))
            tail_type = handle_expr_context(ctx.expr(1))
            if not isinstance(tail_type, ListType):
                type_error(ERROR_UNEXPECTED_LIST)
            if tail_type.elem_type is None:
                tail_type.elem_type = head_type
            elif tail_type.elem_type != head_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return tail_type

        case stellaParser.HeadContext():
            expr_type = handle_expr_context(ctx.expr())
            if not isinstance(expr_type, ListType):
                type_error(ERROR_NOT_A_LIST)
            return expr_type.elem_type

        case stellaParser.TailContext():
            expr_type = handle_expr_context(ctx.expr())
            if not isinstance(expr_type, ListType):
                type_error(ERROR_NOT_A_LIST)
            return expr_type

        case stellaParser.IsEmptyContext():
            expr_type = handle_expr_context(ctx.expr())
            if isinstance(expr_type, PanicType):
                type_error(ERROR_AMBIGUOUS_PANIC_TYPE)
            if not isinstance(expr_type, ListType):
                type_error(ERROR_NOT_A_LIST)
            if expr_type.elem_type is None:
                type_error(ERROR_AMBIGUOUS_LIST_TYPE)
            return BoolType()

        case stellaParser.ParenthesisedExprContext():
            return handle_expr_context(ctx.expr())

        case stellaParser.VariantContext():
            label = ctx.label.text
            expr_type = handle_expr_context(ctx.expr())

            print(f"Handling variant expression with label '{label}' and type '{expr_type}'")

            ascribed_type = None
            if isinstance(ctx.parentCtx, stellaParser.TypeAscContext):
                ascribed_type = parse_type(ctx.parentCtx.stellatype())
            elif isinstance(ctx.parentCtx, stellaParser.ApplicationContext):
                func_type = handle_expr_context(ctx.parentCtx.expr(0))
                if isinstance(func_type, FunType) and isinstance(func_type.param_types[0], TypeVariant):
                    ascribed_type = func_type.param_types[0]

            if ascribed_type is None or not isinstance(ascribed_type, TypeVariant):
                type_error(ERROR_AMBIGUOUS_VARIANT_TYPE)

            if label not in ascribed_type.fields:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            expected_type = ascribed_type.fields[label]
            print(f"Expected type for label '{label}': {expected_type}")

            if expr_type != expected_type:
                print(f"Type mismatch for variant label '{label}': expected '{expected_type}', got '{expr_type}'")
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return ascribed_type

        case stellaParser.PatternVariantContext():
            label = ctx.label.text
            pattern_type = handle_expr_context(ctx.pattern())
            expected_type = None
            if isinstance(pattern_type, TypeVariant):
                if label in pattern_type.fields:
                    expected_type = pattern_type.fields[label]
                else:
                    type_error(ERROR_UNEXPECTED_VARIANT_LABEL)
            else:
                type_error(ERROR_UNEXPECTED_VARIANT)

            body_type = handle_expr_context(ctx.expr())
            return body_type

        case stellaParser.FixContext():
            expr_type = handle_expr_context(ctx.expr())
            if not isinstance(expr_type, FunType):
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            if len(expr_type.param_types) != 1:
                type_error(ERROR_INCORRECT_NUMBER_OF_ARGUMENTS)

            return_type = expr_type.return_type
            param_type = expr_type.param_types[0]

            if return_type != param_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return return_type

        case stellaParser.SequenceContext():
            first_expr_type = handle_expr_context(ctx.expr(0))
            second_expr_type = handle_expr_context(ctx.expr(1))
            return second_expr_type

        case stellaParser.RefContext():
            expr_type = handle_expr_context(ctx.expr())
            return RefType(expr_type)

        case stellaParser.DerefContext():
            expr_type = handle_expr_context(ctx.expr())
            if not isinstance(expr_type, RefType):
                type_error(ERROR_NOT_A_REFERENCE)
            return expr_type.ref_type

        case stellaParser.AssignContext():
            ref_type = handle_expr_context(ctx.expr(0))
            value_type = handle_expr_context(ctx.expr(1))
            if not isinstance(ref_type, RefType):
                type_error(ERROR_NOT_A_REFERENCE)
            if ref_type.ref_type != value_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)
            return UnitType()

        case stellaParser.PanicContext():
            print("Detected panic expression")
            if isinstance(ctx.parentCtx,
                          (stellaParser.ApplicationContext, stellaParser.ListContext, stellaParser.MatchContext)):
                type_error(ERROR_AMBIGUOUS_PANIC_TYPE)
            return PanicType()

        case stellaParser.ThrowContext():
            print("Handling throw expression")
            exception_expr_type = handle_expr_context(ctx.expr())
            print(f"Throwing expression type: {exception_expr_type}")

            if isinstance(ctx.parentCtx, stellaParser.ApplicationContext):
                type_error(ERROR_AMBIGUOUS_THROW_TYPE)

            print(f"Exception environment: {exception_env}")

            matched = False
            for exception_name, exception_type in exception_env.items():
                print(f"Checking against registered exception: {exception_name} = {exception_type}")

                if isinstance(exception_expr_type, TypeVariant):
                    print(f"Found variant type: {exception_expr_type}")
                    for field_name, field_type in exception_expr_type.fields.items():
                        print(f"Field name: {field_name}, Field type: {field_type}")

                    if "good" in exception_expr_type.fields:
                        field_type = exception_expr_type.fields["good"]
                        print(f"Found 'good' field with type: {field_type}")

                        if isinstance(field_type, BoolType):
                            print(f"'good' field is of type Bool, which matches.")
                            matched = True
                            break
                        else:
                            print(f"'good' field is not Bool, it is {field_type}")
                    else:
                        print(f"No 'good' field in variant. Available fields: {exception_expr_type.fields}")

                if isinstance(exception_expr_type, TypeVariant) and isinstance(exception_type, TypeVariant):
                    print(f"Checking fields for variant type: {exception_expr_type}")
                    match = True
                    for label, expr_field_type in exception_expr_type.fields.items():
                        if label in exception_type.fields:
                            declared_field_type = exception_type.fields[label]
                            print(
                                f"Field '{label}': expression type = {expr_field_type}, declared type = {declared_field_type}")
                            if expr_field_type != declared_field_type:
                                print(f"Type mismatch for field '{label}': {expr_field_type} != {declared_field_type}")
                                match = False
                                break
                        else:
                            #print(
                                #f"Field '{label}' not found in declared exception type. Available fields: {exception_type.fields}")
                            match = False
                            break

                    if match:
                        print(f"Matched exception type: {exception_name}")
                        matched = True
                        break

                elif isinstance(exception_expr_type, NatType) and isinstance(exception_type, NatType):
                    print(f"Matched exception type: {exception_name}")
                    matched = True
                    break

            if matched:
                print("Throw expression matched, returning PanicType")
                return PanicType()
            else:
                print(f"Failed to match exception type: {exception_expr_type}")
                type_error(ERROR_EXCEPTION_TYPE_NOT_DECLARED)

        case stellaParser.TryWithContext():
            print("Detected try-with expression")
            try_expr_type = handle_expr_context(ctx.expr(0))
            handler_expr_type = handle_expr_context(ctx.expr(1))

            if try_expr_type != handler_expr_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return try_expr_type

        case stellaParser.TryCatchContext():
            print("Detected try-catch expression")

            try_expr_type = handle_expr_context(ctx.expr(0))
            print(f"Type of try block: {try_expr_type}")

            catch_expr = ctx.expr(1)
            catch_pattern = ctx.pattern().getText()
            print(f"Handling catch block with pattern: {catch_pattern}")

            exception_type = exception_env.get("exception")
            if exception_type is None:
                type_error(ERROR_EXCEPTION_TYPE_NOT_DECLARED)
            type_env[catch_pattern] = exception_type

            catch_expr_type = handle_expr_context(catch_expr)
            print(f"Type of catch block: {catch_expr_type}")

            if try_expr_type != catch_expr_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            return try_expr_type

        case stellaParser.ConstMemoryContext():
            if isinstance(ctx.parentCtx, stellaParser.DerefContext):
                expected_type = RefType(NatType())
                print(f"Assuming type of memory address as: {expected_type}")
                return expected_type
            else:
                type_error(ERROR_AMBIGUOUS_REFERENCE_TYPE)

        case _:
            print(f"Unhandled expression context: {ctx.getText()} of type {type(ctx).__name__}")
            type_error("Unsupported expression")


def handle_decl_context(ctx: stellaParser.DeclContext):
    declaration_text = ctx.getText()
    print(f"Handling declaration: {declaration_text}")

    #print(f"Available attributes and methods for ctx: {dir(ctx)}")

    match ctx:
        case stellaParser.DeclFunContext():
            name = cast(Token, ctx.name).text
            print(f"Declaring function: {name}")

            param_decls = ctx.paramDecls
            param_types = []
            for param_decl in param_decls:
                param_name = param_decl.name.text
                param_type_ctx = param_decl.stellatype()
                param_type = parse_type(param_type_ctx)

                print(f"Adding parameter '{param_name}' of type '{param_type}' to type environment.")
                type_env[param_name] = param_type
                param_types.append(param_type)

            return_type_ctx = ctx.returnType
            return_type = parse_type(return_type_ctx)

            func_type = FunType(param_types, return_type)
            type_env[name] = func_type

            return_expr = cast(stellaParser.ExprContext, ctx.returnExpr)
            expr_type = handle_expr_context(return_expr)
            print(f"Expected return type: {return_type}, Actual return type: {expr_type}")
            if not isinstance(expr_type, PanicType) and expr_type != return_type:
                type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)

            print(f"Function {name} type-checked successfully.")

        case stellaParser.DeclExceptionTypeContext():
            print("Handling exception type declaration!")

            try:
                exception_name = ctx.getChild(0).getText()
                print(f"Extracted exception name: {exception_name}")
            except AttributeError:
                print("Failed to extract exception name.")
                return

            try:
                if ctx.stellatype() is not None:
                    exception_type = parse_type(ctx.stellatype())
                    exception_env[exception_name] = exception_type
                    print(f"Declared exception type: {exception_name} = {exception_type}")
                else:
                    print("Error: Missing exception type.")
            except AttributeError:
                print("Failed to extract exception type.")
                return

        case _:
            print(f"Unknown declaration type: {ctx.getText()}")


def parse_type(ctx: stellaParser.StellatypeContext) -> Type:
    if isinstance(ctx, stellaParser.TypeNatContext):
        return NatType()
    elif isinstance(ctx, stellaParser.TypeBoolContext):
        return BoolType()
    elif isinstance(ctx, stellaParser.TypeUnitContext):
        return UnitType()
    elif isinstance(ctx, stellaParser.TypeFunContext):
        param_types = [parse_type(param_type) for param_type in ctx.stellatype()[:-1]]
        return_type = parse_type(ctx.stellatype()[-1])
        if len(param_types) == 0:
            return FunType([], return_type)

        return FunType(param_types, return_type)
    elif isinstance(ctx, stellaParser.TypeTupleContext):
        elem_types = [parse_type(t) for t in ctx.stellatype()]
        return TupleType(elem_types)
    elif isinstance(ctx, stellaParser.TypeRecordContext):
        fields = {field.label.text: parse_type(field.stellatype()) for field in ctx.fieldTypes}
        return RecordType(fields)
    elif isinstance(ctx, stellaParser.TypeParensContext):
        inner_type_ctx = ctx.stellatype()
        return parse_type(inner_type_ctx)
    elif isinstance(ctx, stellaParser.TypeSumContext):
        left_type = parse_type(ctx.stellatype(0))
        right_type = parse_type(ctx.stellatype(1))
        return SumType(left_type, right_type)
    elif isinstance(ctx, stellaParser.TypeListContext):
        elem_type = parse_type(ctx.stellatype())
        return ListType(elem_type)
    elif isinstance(ctx, stellaParser.TypeVariantContext):
        fields = {field.label.text: parse_type(field.stellatype()) for field in
                  ctx.variantFieldType()}
        return TypeVariant(fields)
    elif isinstance(ctx, stellaParser.TypeRefContext):
        ref_type = parse_type(ctx.stellatype())
        return RefType(ref_type)
    else:
        type_error("Unsupported type")


def parse_base_type(type_str: str) -> Type:
    if type_str == "Nat":
        return NatType()
    elif type_str == "Bool":
        return BoolType()
    else:
        type_error(ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION)


def handle_program_context(ctx: stellaParser.ProgramContext):
    print("Handling program context")
    main_found = False

    for decl in ctx.decls:
        if isinstance(decl, stellaParser.DeclFunContext):
            name = cast(Token, decl.name).text
            return_type_ctx = decl.returnType
            return_type = parse_type(return_type_ctx)
            param_decls = decl.paramDecls
            param_types = [parse_type(param_decl.stellatype()) for param_decl in param_decls]
            func_type = FunType(param_types, return_type)
            type_env[name] = func_type
            if name == 'main':
                main_found = True

    for decl in ctx.decls:
        handle_decl_context(decl)

    if not main_found:
        type_error(ERROR_MISSING_MAIN)


def print_ast(node, level=0):
    indent = "  " * level
    if hasattr(node, 'getText'):
        print(f"{indent}{type(node).__name__}: {node.getText()}")
    else:
        print(f"{indent}{type(node).__name__}")

    if hasattr(node, 'getChildren'):
        for child in node.getChildren():
            print_ast(child, level + 1)


def main(argv):
    print("Starting type checker")
    if sys.version_info.major < 3 or sys.version_info.minor < 10:
        raise RuntimeError('Python 3.10 or a more recent version is required.')
    if len(argv) > 1:
        input_stream = FileStream(argv[1])
    else:
        input_stream = StdinStream()

    add_standard_functions_to_env()
    lexer = stellaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = stellaParser(stream)
    program = parser.program()

    # print("AST:")
    #print_ast(program)

    handle_program_context(program)


if __name__ == "__main__":
    main(sys.argv)
