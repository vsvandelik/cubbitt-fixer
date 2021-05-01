import argparse
from typing import Union, List, Tuple

from ._languages import Languages
from ._numbers_fixer import NumberFixer
from ._decimal_separator_fixer import DecimalSeparatorFixer


class Fixer:
    """Class fixing text with specific fixers based on given parameters.

    For constructing the fixer some arguments are needed.

    List of supported arguments:
      - `source_lang` - text acronym of language of source sentence
      - `target_lang` - text acronym of language of target sentence
      - `approximately` - flag whenever it  should consider approximation phrases
      - `recalculate` - flag whenever it should change correct units into different ones

    :param arguments: object with arguments values
    :type arguments: argparse object
    """

    def __init__(self, arguments: argparse):
        source_lang = Languages.get_language(arguments.source_lang)
        target_lang = Languages.get_language(arguments.target_lang)

        # TODO: More complex arguments (considering desired dialect of units and recalculationg mode)
        # TODO: Exception when languages is not valid

        self.numbers_fixer = NumberFixer(
            arguments.approximately,
            arguments.recalculate,
            source_lang,
            target_lang,
            0.1,
            0.1)

        self.decimal_separator_fixer = DecimalSeparatorFixer(source_lang, target_lang)

    def fix(self, original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Function to fix translation of one sentence based on Fixer attributes.

        It caches all exceptions with fixer and when some exception is cached,
        sentence is marked as unfixable.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
        """
        decimal_repair, marks_separators = self.decimal_separator_fixer.fix(original_text, translated_text)
        translated_text = decimal_repair if isinstance(decimal_repair, str) else translated_text
        repair, marks_numbers = self.numbers_fixer.fix_numbers_problems(original_text, translated_text)

        """
        try:
            decimal_repair, marks_separators = self.decimal_separator_fixer.fix(original_text, translated_text)
            translated_text = decimal_repair if isinstance(decimal_repair, str) else translated_text
            repair, marks_numbers = self.numbers_fixer.fix_numbers_problems(original_text, translated_text)
        except Exception as e:
            print(e)
            print(original_text)
            print(translated_text)
            print()
            return False, []
        """
        if repair is True and isinstance(decimal_repair, str):
            return decimal_repair, marks_numbers + marks_separators
        else:
            return repair, marks_numbers + marks_separators
