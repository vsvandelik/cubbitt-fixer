from enum import Enum, auto


class FixerStatisticsMarks(Enum):
    """Labels for statistics about fixer"""

    U_SINGLE_NUMBER_SENTENCE = auto()  #: There is only one number in the sentence.
    U_MULTIPLE_NUMBER_SENTENCE = auto()  #: There are multiple numbers in the sentence.
    U_CORRECT_NUMBER_UNIT = auto()  #: The number with unit is correctly translated.
    U_CORRECT_NUMBER_WRONG_UNIT = auto()  #: The number remains but the unit was changed.
    U_WRONG_NUMBER_CORRECT_UNIT = auto()  #: The number was changes but the unit is only translated.
    U_WRONG_NUMBER_UNIT = auto()  #: Both unit and number were changed.
    U_APPLIED_TOLERANCE_RATE = auto()  #: Number is different but within the tolerance given by user.
    U_DIFFERENT_COUNT_NUMBERS = auto()  #: The tool parsed different count of numbers in source and translated sentence.
    U_NUMBER_AS_WORD = auto()  #: The number written as a word.
    U_UNABLE_TO_RECALCULATE = auto()  #: Mode is recalculating but the number cannot be recalculated due some problem.
    U_RECALCULATED = auto()  #: The number was recalculated to another number.
    U_NUMBERS_MODIFIERS = auto()  #: The number is used as modifier in English.
    U_ONLY_NUMBER_SAME = auto()  #: Same numbers without units.
    U_ONLY_NUMBER_DIFFERENT = auto()  #: Numbers without units but different.
    U_SAME_NUMBER_ONLY_UNIT_SRC = auto()  #: The unit was removed by CUBBITT in the translation.
    U_SAME_NUMBER_ONLY_UNIT_TRG = auto()  #: The translator added unit in the translation.
    U_FIXED = auto()  #: The number with unit was fixed.

    G_EXCEPTION_CATCH = auto()  #: Some problem (probably parsing) was caught in fixing process.

    S_SWAPPED_SEPARATORS = auto()  #: The separators was swapped in the translation.
    S_DECIMAL_POINT_AS_TIME = auto()  #: There was a time written as a decimal number.
    S_CORRECT = auto()  #: The separators were correctly translated.

    N_MULTIPLE_NAMES_SENTENCE = auto()  #: There are multiple person's names in the sentence.
    N_PROBLEM_UNFIXABLE = auto()  #: Cannot fix the translated name.
    N_NAME_CORRECT = auto()  #: The name remains in the translation correctly.
    N_NAME_CHANGED = auto()  #: The name was changed in the translation.
    N_SINGLE_NAME_SENTENCE = auto()  #: There is only one person's name.
