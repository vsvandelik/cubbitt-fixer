import re
from typing import Union, List, Tuple

from ._languages import Language
from ._statistics import StatisticsMarks


class DecimalSeparatorFixer:
    """Fixer of wrong translation of decimal / thousands separator

    It checks whenever the translator correctly change decimal separator
    from source language from target language because the separator
    is different in individual languages (eg. in czech is used '.' for
    thousands and ',' for decimal numbers, in english it is the opposite).

    :param source_lang: instance of language of original sentence
    :param target_lang: instance of language of translated sentence
    """

    def __init__(self, source_lang: Language, target_lang: Language):
        self.source_lang = source_lang
        self.target_lang = target_lang

        self.source_pattern = DecimalSeparatorFixer.__prepare_re_pattern_all_numbers(source_lang)
        self.target_pattern = DecimalSeparatorFixer.__prepare_re_pattern_all_numbers(target_lang)

    def fix(self, original_sentence: str, translated_sentence: str) -> Tuple[Union[str, bool], List]:
        """It verifies whenever the sentence contains problem and tries to fix it

        Based on regular expression it searches for numbers with separator in source language
        and verifies whenever same numbers with correct separators are in the translation.

        :param original_sentence: sentence in source language
        :param translated_sentence: sentence translation from translator
        """

        source_parts = re.finditer(self.source_pattern, original_sentence)

        replaced = 0

        for number in source_parts:
            number = number["number"]

            same_in_translation = re.search(DecimalSeparatorFixer.__prepare_re_patter_one_number(number, self.target_lang), translated_sentence)
            if same_in_translation:
                translated_sentence = translated_sentence.replace(number, DecimalSeparatorFixer.__swap_separators(number))
                replaced += 1

        if replaced == 0:
            return True, []
        else:
            return translated_sentence, [StatisticsMarks.DECIMAL_SEPARATOR_PROBLEM]

    @staticmethod
    def __prepare_re_patter_one_number(number: str, language: Language) -> str:
        """Returns raw regex pattern searching for the number"""
        thousands_sep = re.escape(language.thousands_separator)
        decimal_sep = re.escape(language.decimal_separator)
        number = re.escape(number)

        return rf"([^0-9{thousands_sep}{decimal_sep}]|^){number}(\.$|,? [^0-9]|$)"

    @staticmethod
    def __prepare_re_pattern_all_numbers(language: Language) -> re.Pattern:
        """Compile regex patter based on given language"""
        thousands_sep = re.escape(language.thousands_separator)
        decimal_sep = re.escape(language.decimal_separator)

        numbers_thousands_decimal_separator = r"(\d+([" + thousands_sep + "]\d{3})*" + decimal_sep + "\d+)"
        numbers_thousands_separator = r"(\d+([" + thousands_sep + "]\d{3})+)"

        return re.compile(f"([^0-9{thousands_sep}{decimal_sep}]|^)"  # before number
                          f"(?P<number>{numbers_thousands_decimal_separator}|{numbers_thousands_separator})"
                          "(\.$|,? [^0-9]|$)"  # after number
                          )

    @staticmethod
    def __swap_separators(number: str) -> str:
        """Swap comma and dot"""
        number = number.replace(',', '<>')
        number = number.replace('.', ',')
        return number.replace('<>', '.')
