from ._custom_types import *
from ._units import Unit


class Replacer:
    """Supporting class for replacing strings in broken sentences

    The class contains static methods for specific replacement algorithms.
    """

    @staticmethod
    def replace_unit(sentence: str, number_unit_part: str, number: Number, unit: Unit, new_unit: Unit) -> str:
        """Replace only unit within the broken sentence

        Based on new unit it decides whenever the unit should be put. When the new unit
        has flag "before number", the replacer returns unit before number.

        For units before number with length 1 there is no space between unit and number.
        For units after number there is number is first letter of unit is alphabet char.

        :param sentence: broken sentence
        :param number_unit_part: part of the broken sentence with number and broken unit
        :param number: parsed number
        :param unit: parsed unit
        :param new_unit: unit to replace with
        :return: sentence with replaced unit
        """

        translated_number = number_unit_part.replace(unit.word, "").strip(' ,-')

        if new_unit.before_number and len(new_unit.word) == 1:
            new_number_unit_part = f"{new_unit.word}{translated_number}"
        elif new_unit.before_number:
            new_number_unit_part = f"{new_unit.word} {translated_number}"
        elif not new_unit.word[0].isalpha():
            new_number_unit_part = f"{translated_number}{new_unit.word}"
        else:
            new_number_unit_part = f"{translated_number} {new_unit.word}"

        return sentence.replace(number_unit_part, new_number_unit_part)
