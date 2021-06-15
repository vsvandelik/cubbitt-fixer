from enum import Enum, auto


class StatisticsMarks(Enum):
    """Labels for statistics about fixer"""

    SINGLE_NUMBER_UNIT_SENTENCE = auto()
    MULTIPLE_NUMBER_UNIT_SENTENCE = auto()
    CORRECT_NUMBER_UNIT = auto()
    CORRECT_NUMBER_WRONG_UNIT = auto()
    WRONG_NUMBER_CORRECT_UNIT = auto()
    WRONG_NUMBER_UNIT = auto()
    APPLIED_TOLERANCE_RATE = auto()
    DECIMAL_SEPARATOR_PROBLEM = auto()
    DIFFERENT_COUNT_NUMBERS_UNITS = auto()
    NUMBER_AS_WORD = auto()
    UNFIXABLE_PART = auto()
    EXCEPTION_CATCH = auto()
    UNABLE_TO_RECALCULATE = auto()
    RECALCULATED = auto()
    MULTIPLE_NAMES_SENTENCE = auto()
    NAMES_PROBLEM_UNFIXABLE = auto()
    NAMES_CORRECT = auto()
    SINGLE_NAME_SENTENCE = auto()
    NUMBERS_MODIFIERS = auto()
