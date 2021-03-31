import argparse
from typing import Union, List, Tuple

from ._languages import Languages
from ._numbers_fixer import NumberFixer



class Fixer:
    """Class fixing text with specific fixers based on given parameters."""

    def __init__(self, arguments: argparse):
        source_lang = Languages.get_language(arguments.source_lang)
        target_lang = Languages.get_language(arguments.target_lang)

        # TODO: Exception when languages is not valid

        self.numbers_fixer = NumberFixer(
            arguments.approximately,
            arguments.recalculate,
            source_lang,
            target_lang)

    def fix(self, original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Function to fix translation of one sentence based on Fixer attributes.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: repaired text if sentence can be fixed, True if sentence is correct, False if sentence cannot be repaired
        :rtype: str or bool
        """
        try:
            repair = self.numbers_fixer.fix_numbers_problems(original_text, translated_text)
        except Exception:
            return False, []

        return repair


'''
    @staticmethod
    def __generate_translated_variants(number: int, rest: Unit, language: Language) -> List[str]:
        """Generates all possible variants (cartesian product) of number with unit.

        Actual supported patterns are:
          - 25cm
          - 25 cm
          - 25-cm

        :param number: Int or float number
        :param rest: Unit to be added to number
        :param language: Language of unit
        :return: List of all variants
        :rtype: List of str
        """

        patterns = ["{}{}", "{} {}", "{}-{}"]
        rests = []

        numbers = [number, '{:,}'.format(number)]
        if language.acronym == 'cs' and number in dt.en.keys():  # rewrite digit as a string
            numbers.append(dt.en[number])
            rests = [rest.word] + units.get_words_by_category_language(rest.category, language)
        elif language.acronym == 'en' and number in dt.cs.keys():
            numbers.append(dt.cs[number])
            rests = [rest.word] + units.get_words_by_category_language(rest.category, language)

        variants = []

        for pat in patterns:
            for num in numbers:
                for res in rests:
                    variants.append(pat.format(num, res))

        return variants
'''
