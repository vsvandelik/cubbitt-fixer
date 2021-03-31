from enum import Enum


class StatisticsMarks(Enum):
    """Labels for statistics about fixer"""

    SINGLE_NUMBER_UNIT_SENTENCE = 0
    MULTIPLE_NUMBER_UNIT_SENTENCE = 1
    CORRECT_NUMBER_UNIT = 2
    CORRECT_NUMBER_WRONG_UNIT = 3
    WRONG_NUMBER_CORRECT_UNIT = 4
    DECIMAL_SEPARATOR_PROBLEM = 5
    CORRECT_MULTIPLE_NUMBER_UNIT_SENTENCE = 6
