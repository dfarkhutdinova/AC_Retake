from stella_types import *
from typechecker import typecheck_program, TYPE_BOOL, TYPE_NAT

def main():
    try:
        # Test 1: Simple function declaration with a constant return value
        func1 = DeclFun(
            name='main',
            parameters=[Parameter(name='x', param_type=TYPE_NAT)],
            return_value=ConstInt(),
            return_type=TYPE_NAT
        )

        program1 = Program(declarations=[func1])
        print("Test 1: Simple function declaration with a constant return value")
        typecheck_program(program1)
        print("Test 1 passed.\n")

    except Exception as e:
        print(f"Test 1 failed: {e}\n")

    try:
        # Test 2: Function with variable and Succ expression
        func2 = DeclFun(
            name='main',
            parameters=[Parameter(name='x', param_type=TYPE_NAT)],
            return_value=Succ(Var('x')),
            return_type=TYPE_NAT
        )

        program2 = Program(declarations=[func2])
        print("Test 2: Function with variable and Succ expression")
        typecheck_program(program2)
        print("Test 2 passed.\n")

    except Exception as e:
        print(f"Test 2 failed: {e}\n")

    try:
        # Test 3: If expression
        func3 = DeclFun(
            name='main',
            parameters=[Parameter(name='x', param_type=TYPE_NAT)],
            return_value=If(ConstBool(), ConstInt(), Var('x')),
            return_type=TYPE_NAT
        )

        program3 = Program(declarations=[func3])
        print("Test 3: If expression")
        typecheck_program(program3)
        print("Test 3 passed.\n")

    except Exception as e:
        print(f"Test 3 failed: {e}\n")

    try:
        # Test 4: Nested function application
        func4 = DeclFun(
            name='main',
            parameters=[Parameter(name='x', param_type=TYPE_NAT)],
            return_value=Application(
                Abstraction([Parameter(name='y', param_type=TYPE_NAT)], Var('y')),
                [Var('x')]
            ),
            return_type=TYPE_NAT
        )

        program4 = Program(declarations=[func4])
        print("Test 4: Nested function application")
        typecheck_program(program4)
        print("Test 4 passed.\n")

    except Exception as e:
        print(f"Test 4 failed: {e}\n")

    try:
        # Test 5: NatRec expression
        func5 = DeclFun(
            name='main',
            parameters=[Parameter(name='x', param_type=TYPE_NAT)],
            return_value=NatRec(
                Var('x'),
                ConstInt(),
                Abstraction([Parameter(name='n', param_type=TYPE_NAT)], Succ(Var('n')))
            ),
            return_type=TYPE_NAT
        )

        program5 = Program(declarations=[func5])
        print("Test 5: NatRec expression")
        typecheck_program(program5)
        print("Test 5 passed.\n")

    except Exception as e:
        print(f"Test 5 failed: {e}\n")

if __name__ == "__main__":
    main()
