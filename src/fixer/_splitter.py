from typing import Tuple, List

from ._custom_types import Number
from ._languages import Language
from ._units import Unit, units


class StringToNumberUnitConverter:
    """Supporting class for processing string with number and unit into separate parts."""

    @staticmethod
    def split_number_unit(text: str, language: Language, *, custom_separator: str = None) -> Tuple[Number, Unit]:
        """Split number-unit sentence part into separate variables.

        Number is parsed as a float or int. It uses language specific decimal separator.

        :param text: Part of the sentence to split.
        :param language: Language of the text
        :param custom_separator: Keyword-only parameter for specifying custom decimal separator
        :return: Tuple with number and unit as it was split
        """

        if not custom_separator:
            custom_separator = language.decimal_separator

        if '"' in text or "'" in text:
            return StringToNumberUnitConverter.__convert_text_to_inches(text), units.get_unit_by_word('inch', language)

        # fix of situation: "Back in 1892, 250 kilometres"
        multiple_sentences_split = text.strip(' .,- ').split(', ')
        if len(multiple_sentences_split) > 1:
            text = multiple_sentences_split[-1]

        if text[0].isdigit():
            number_string, decimal, unit = StringToNumberUnitConverter.__split_string_number_first(text, custom_separator)
        else:
            number_string, decimal, unit = StringToNumberUnitConverter.__split_string_unit_first(text, custom_separator)

        number_string = "".join(number_string)
        """
        idx_dec_sep = number_string.find(language.decimal_separator)
        idx_ths_sep = number_string.find(language.thousands_separator)
        if idx_dec_sep > -1 and idx_ths_sep > -1 and idx_dec_sep < idx_ths_sep:
            number_string = DecimalSeparatorFixer.swap_separators(number_string)
        """
        if decimal:
            number = float(number_string)
        else:
            number = int(number_string)

        unit = units.get_unit_by_word(unit, language)

        return number, unit

    @staticmethod
    def __split_string_number_first(text: str, custom_separator: str) -> Tuple[List[str], bool, str]:
        """Parse "250 km" to number and unit, verifies whenever the number is decimal"""
        number_string = []
        decimal = False
        unit = None

        for idx, ch in enumerate(text):
            if ch.isdigit():
                number_string.append(ch)
            elif ch == custom_separator:
                number_string.append('.')
                decimal = True
            elif ch.isalpha() or ch in units.get_single_char_units_symbols() or ch == '°':
                unit = text[idx:].strip(' -')
                break

        return number_string, decimal, unit

    @staticmethod
    def __split_string_unit_first(text: str, custom_separator: str) -> Tuple[List[str], bool, str]:
        """Parse "$250" to unit and number, verifies whenever the number is decimal"""
        number_string = []
        decimal = False
        unit = None

        unit_complete = False
        for idx, ch in enumerate(text):
            if ch.isdigit() and unit_complete is False:
                unit = text[:idx].strip(' -')
                unit_complete = True
                number_string.append(ch)
            elif ch.isdigit():
                number_string.append(ch)
            elif ch == custom_separator and idx < len(text) - 1:
                number_string.append('.')
                decimal = True

        return number_string, decimal, unit

    @staticmethod
    def extract_string_number_from_number_unit_string(text: str) -> str:
        # fix of situation: "Back in 1892, 250 kilometres"
        multiple_sentences_split = text.split(', ')
        if len(multiple_sentences_split) > 1:
            text = multiple_sentences_split[-1]

        if not text[0].isdigit():
            start = None
            for idx, char in enumerate(text):
                if not start and char.isdigit():
                    start = idx
                if start and char.isalpha():  # for eg. CZK 250 million -> get only 250
                    return text[start:idx]

            return text[start:]

        else:
            for idx, char in enumerate(text):
                if char.isalpha():
                    return text[:idx].strip()

    @staticmethod
    def __convert_text_to_inches(text: str) -> int:
        """Convert number written as feet and inches (6'12") to inches"""
        feet = 0
        feet_idx_end = None
        inches = 0
        for idx, l in enumerate(text):
            if l == "'":
                feet = int(text[:idx])
                feet_idx_end = idx
            elif l == '"':
                inches = int(text[feet_idx_end + 1:idx])

        return inches + 12 * feet
