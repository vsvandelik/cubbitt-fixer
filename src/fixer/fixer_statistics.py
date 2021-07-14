from enum import Enum, auto


class FixerStatisticsMarks(Enum):
    """Labels for statistics about fixer"""

    U_SINGLE_NUMBER_SENTENCE = auto()  #: :meta hide-value:
    U_MULTIPLE_NUMBER_SENTENCE = auto()  #: :meta hide-value:
    U_CORRECT_NUMBER_UNIT = auto()  #: :meta hide-value:
    U_CORRECT_NUMBER_WRONG_UNIT = auto()  #: :meta hide-value:
    U_WRONG_NUMBER_CORRECT_UNIT = auto()  #: :meta hide-value:
    U_WRONG_NUMBER_UNIT = auto()  #: :meta hide-value:
    U_APPLIED_TOLERANCE_RATE = auto()  #: :meta hide-value:
    U_DIFFERENT_COUNT_NUMBERS = auto()  #: :meta hide-value:
    U_NUMBER_AS_WORD = auto()  #: :meta hide-value:
    U_UNABLE_TO_RECALCULATE = auto()  #: :meta hide-value:
    U_RECALCULATED = auto()  #: :meta hide-value:
    U_NUMBERS_MODIFIERS = auto()  #: :meta hide-value:
    U_ONLY_NUMBER_SAME = auto()  #: :meta hide-value:
    U_ONLY_NUMBER_DIFFERENT = auto()  #: :meta hide-value:
    U_FIXED = auto()  #: :meta hide-value:

    G_EXCEPTION_CATCH = auto()  #: :meta hide-value:

    S_SWAPPED_SEPARATORS = auto()  #: :meta hide-value:
    S_DECIMAL_POINT_AS_TIME = auto()  #: :meta hide-value:

    N_MULTIPLE_NAMES_SENTENCE = auto()  #: :meta hide-value:
    N_PROBLEM_UNFIXABLE = auto()  #: :meta hide-value:
    N_NAME_CORRECT = auto()  #: :meta hide-value:
    N_NAME_CHANGED = auto()  #: :meta hide-value:
    N_SINGLE_NAME_SENTENCE = auto()  #: :meta hide-value:
