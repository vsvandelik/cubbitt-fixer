import re
from typing import Union, List, Tuple

from ._sentence_pair import SentencePair

from ._languages import Language
from ._statistics import StatisticsMarks
from .fixer_configurator import FixerConfigurator


class DecimalSeparatorFixer:
    """Fixer of wrong translation of decimal / thousands separator

    It checks whenever the translator correctly change decimal separator
    from source language from target language because the separator
    is different in individual languages (eg. in czech is used '.' for
    thousands and ',' for decimal numbers, in english it is the opposite).
    """

    def __init__(self, configuration: FixerConfigurator):
        self.configuration = configuration

        self.source_lang = configuration.source_lang
        self.target_lang = configuration.target_lang

        self.source_pattern = DecimalSeparatorFixer.__prepare_re_pattern_all_numbers(self.source_lang)
        self.target_pattern = DecimalSeparatorFixer.__prepare_re_pattern_all_numbers(self.target_lang)

    def fix(self, sentence_pair: SentencePair) -> Tuple[Union[str, bool], List]:
        """It verifies whenever the sentence contains problem and tries to fix it

        Based on regular expression it searches for numbers with separator in source language
        and verifies whenever same numbers with correct separators are in the translation.

        """

        source_parts = re.finditer(self.source_pattern, sentence_pair.source_text)

        replaced = 0
        translated_sentence = sentence_pair.target_text

        for number in source_parts:
            number = number["number"]

            same_in_translation = re.search(DecimalSeparatorFixer.__prepare_re_patter_one_number(number, self.target_lang), translated_sentence)
            if same_in_translation:
                translated_sentence = translated_sentence.replace(number, DecimalSeparatorFixer.swap_separators(number))
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
    def swap_separators(number: str) -> str:
        """Swap comma and dot"""
        number = number.replace(',', '<>')
        number = number.replace('.', ',')
        return number.replace('<>', '.')
