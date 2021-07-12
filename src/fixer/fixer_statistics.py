from enum import Enum, auto


class FixerStatisticsMarks(Enum):
    """Labels for statistics about fixer"""

    SINGLE_NUMBER_UNIT_SENTENCE = auto()  #: :meta hide-value:
    MULTIPLE_NUMBER_UNIT_SENTENCE = auto()  #: :meta hide-value:
    CORRECT_NUMBER_UNIT = auto()  #: :meta hide-value:
    CORRECT_NUMBER_WRONG_UNIT = auto()  #: :meta hide-value:
    WRONG_NUMBER_CORRECT_UNIT = auto()  #: :meta hide-value:
    WRONG_NUMBER_UNIT = auto()  #: :meta hide-value:
    APPLIED_TOLERANCE_RATE = auto()  #: :meta hide-value:
    DECIMAL_SEPARATOR_PROBLEM = auto()  #: :meta hide-value:
    DIFFERENT_COUNT_NUMBERS_UNITS = auto()  #: :meta hide-value:
    NUMBER_AS_WORD = auto()  #: :meta hide-value:
    UNFIXABLE_PART = auto()  #: :meta hide-value:
    EXCEPTION_CATCH = auto()  #: :meta hide-value:
    UNABLE_TO_RECALCULATE = auto()  #: :meta hide-value:
    RECALCULATED = auto()  #: :meta hide-value:
    MULTIPLE_NAMES_SENTENCE = auto()  #: :meta hide-value:
    NAMES_PROBLEM_UNFIXABLE = auto()  #: :meta hide-value:
    NAMES_CORRECT = auto()  #: :meta hide-value:
    SINGLE_NAME_SENTENCE = auto()  #: :meta hide-value:
    NUMBERS_MODIFIERS = auto()  #: :meta hide-value:
    DECIMAL_POINT_AS_TIME = auto()  #: :meta hide-value:
    ONLY_NUMBER_SAME = auto()  #: :meta hide-value:
    ONLY_NUMBER_DIFFERENT = auto()  #: :meta hide-value:
