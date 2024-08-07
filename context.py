from typing import Dict
from stella_types import Type

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
