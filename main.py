from stella_types import Program, DeclFun, Param, Var, Succ, ConstInt, ConstBool, If, NatIsZero, NatRec, Abstraction, TypeNat, TypeBool, TypeRecord
from typechecker import typecheck_program

TYPE_NAT = TypeNat()
TYPE_BOOL = TypeBool()

# Примеры программ на языке Stella

# Пример 1: Простая программа с функцией, возвращающей следующее значение
program1 = Program([
    DeclFun(
        name='main',
        parameters=[Param(name='x', param_type=TYPE_NAT)],
        return_type=TYPE_NAT,
        return_value=Succ(Var('x'))
    )
])

# Пример 2: Программа с функцией, возвращающей константу
program2 = Program([
    DeclFun(
        name='main',
        parameters=[Param(name='x', param_type=TYPE_NAT)],
        return_type=TYPE_NAT,
        return_value=ConstInt(42)
    )
])

# Пример 3: Программа с условным выражением
program3 = Program([
    DeclFun(
        name='main',
        parameters=[Param(name='x', param_type=TYPE_NAT)],
        return_type=TYPE_NAT,
        return_value=If(
            condition=ConstBool(True),
            then_expr=ConstInt(1),
            else_expr=ConstInt(0)
        )
    )
])

# Пример 4: Рекурсивная функция факториала
program4 = Program([
    DeclFun(
        name='main',
        parameters=[Param(name='n', param_type=TYPE_NAT)],
        return_type=TYPE_NAT,
        return_value=If(
            condition=NatIsZero(Var('n')),
            then_expr=ConstInt(1),
            else_expr=NatRec(
                n=Var('n'),
                initial=ConstInt(1),
                step=Abstraction(
                    parameters=[Param(name='i', param_type=TYPE_NAT), Param(name='res', param_type=TYPE_NAT)],
                    return_value=Succ(Var('res'))
                )
            )
        )
    )
])

# Пример 5: Программа с типом суммы (Bool)
program5 = Program([
    DeclFun(
        name='main',
        parameters=[Param(name='b', param_type=TYPE_BOOL)],
        return_type=TYPE_BOOL,
        return_value=If(
            condition=Var('b'),
            then_expr=ConstBool(False),
            else_expr=ConstBool(True)
        )
    )
])

# # Пример 6: Программа с записью (Record)
# program6 = Program([
#     DeclFun(
#         name='main',
#         parameters=[Param(name='r', param_type=TypeRecord(fields={'x': TYPE_NAT, 'y': TYPE_BOOL}))],
#         return_type=TYPE_NAT,
#         return_value=Var('r').fields['x']
#     )
# ])

# Запуск тестов
programs = [program1, program2, program3, program4, program5]

for i, program in enumerate(programs, start=1):
    print(f"Running typecheck on program {i}")
    try:
        typecheck_program(program)
        print(f"Program {i} typechecks successfully!")
    except Exception as e:
        print(f"Program {i} failed to typecheck: {e}")
