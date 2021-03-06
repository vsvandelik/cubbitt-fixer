import argparse
import re
from typing import Union, Optional, List, Tuple

import _digits_translation as dt
import _units

Number = Union[int, float]


class Fixer:
    """Class fixing text with specific fixers based on given parameters."""

    def __init__(self, arguments: argparse):
        self.numbers_fixer = NumberFixer(
            arguments.approximately,
            arguments.recalculate,
            arguments.source_lang,
            arguments.target_lang)

    def fix(self, original_text: str, translated_text: str) -> Union[str, bool]:
        """Function to fix translation of one sentence based on Fixer attributes.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: repaired text if sentence can be fixed, True if sentence is correct, False if sentence cannot be repaired
        :rtype: str or bool
        """
        repair = self.numbers_fixer.fix_numbers_problems(original_text, translated_text)

        return repair


class NumberFixer:
    """Fixer for problems with numbers with units.

    Checks whenever sentence contains any number-unit mistakes and tries to fix them.
    Currently it supports fixing sentences where is only one number-unit pair.

    Currently implemented fixes:

    - untranslated decimal points marks
    """

    APPROXIMATELY_PHRASES = {
        'cs': ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'],
        'en': ['about', 'around', 'roughly', 'approximately']
    }

    DECIMAL_SEPARATORS = {'cs': ',', 'en': '.'}

    def __init__(self, approximately: bool, recalculate: bool, source_lang: str, target_lang: str):
        self.approximately = approximately
        self.recalculate = recalculate

        self.source_lang = source_lang
        self.target_lang = target_lang

        # preparing regex patterns based on supported units
        self.number_patter_source = re.compile(rf"(\d[\d .,]*\s?(?:{_units.units_strings[source_lang]})\b)")
        self.number_patter_target = re.compile(rf"(\d[\d .,]*\s?(?:{_units.units_strings[target_lang]})\b)")

    def fix_numbers_problems(self, original_text: str, translated_text: str) -> Optional[Union[str, bool]]:
        """Fix numbers problems in given sentence based on original text and translated text.

        For supported operations looks at class documentation.

        There are two fixing methods. One for single number problem and the second for the rest. That is because
        there are used different heuristics for each case.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return:
            - fixed sentence
            - True is sentence is correct
            - False is sentence cannot be fixed
            - None if there exists no fixer
        :rtype:
            None if there is any fixer for given sentence
            Bool when the sentence is correct (True) or is unfixable (False)
            Str  when the sentence was fixed
        """
        problems = self.__find_numbers_units(original_text)

        if len(problems) == 1:
            return self.__fix_single_number(problems[0], original_text, translated_text)
        else:
            return None

    def __fix_single_number(self, problem_part, original_text: str, translated_text: str) -> Optional[Union[str,bool]]:
        """Fix sentence with single number problem.

        It searches for matching number in both original and translated text and compares numbers and units.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: repaired sentence or True when sentence is correct or False when sentence cannot be fixed
        :rtype: str or boolean
        """

        (approximately, number, unit) = problem_part

        # find all number-unit pairs in translated text
        translated_parts = re.findall(self.number_patter_target, translated_text)

        fixed_sentence = True

        for translated_part in translated_parts:
            tr_number, tr_unit = self.__split_number_unit(translated_part, self.DECIMAL_SEPARATORS[self.target_lang])

            # verifies if units in original and translated texts are the same
            source_unit_category = _units.units_categories[self.source_lang][unit]
            target_units_in_category = _units.units[source_unit_category][self.target_lang]
            if tr_unit not in target_units_in_category:
                fixed_sentence = False
                # TODO: Recalculating test
                # TODO: Replace with correct unit in a right form

            # verifies if the numbers are the same
            elif number != tr_number:

                # verifies if the problem is caused by untranslated decimal separator
                problem_with_separator = self.__fix_wrong_decimal_separator(number, tr_number, translated_part, translated_text)
                if problem_with_separator:
                    fixed_sentence = problem_with_separator

                else:
                    fixed_sentence = False

                # TODO: Recalculating test

        return fixed_sentence

    def __find_numbers_units(self, text: str) -> List[Tuple[bool, Number, str]]:
        """Search in sentence for number-unit parts

        When some part is found, it is divided into three parts - approximately (whenever the number is precise or not),
        number itself (parsed into int or float) and some unit from list.

        :param text: Sentence to search in.
        :return: All found parts
        :rtype: List of tuples with approximately flag, number and unit
        """
        parts = re.findall(self.number_patter_source, text)
        if len(parts) == 0:  # any number-digit part in original text
            return []

        problems = []
        for part in parts:

            # search for some approximately word before the number
            approximately = False
            if re.search(f"({'|'.join(self.APPROXIMATELY_PHRASES[self.source_lang])}) {part}", text):
                approximately = True

            number, unit = self.__split_number_unit(part, self.DECIMAL_SEPARATORS[self.source_lang])

            problems.append((approximately, number, unit))

        return problems

    def __fix_wrong_decimal_separator(self, number_original: Number, number_translated: Number,
                                      number_unit_translated: str, sentence: str) -> Optional[str]:
        """Verifies if the problem with number is decimal-separator-based and tries to fix it.

        :param number_original: number extracted from original sentence
        :param number_translated: number extracted from translated sentence
        :param number_unit_translated: number-unit part from translated sentence
        :param sentence: full translated sentence
        :return: repaired sentence or None when the sentence is correct
        :rtype: str or None when the sentence does not have problem
        """

        # tries to split number with opposite decimal separator
        tr_number_another_separator, _ = self.__split_number_unit(
            number_unit_translated, self.DECIMAL_SEPARATORS[self.source_lang])

        if number_original == tr_number_another_separator:
            original_string_number = self.__get_string_number(number_unit_translated)

            if isinstance(number_translated, int):
                repaired_string_number = original_string_number.replace(
                    self.DECIMAL_SEPARATORS[self.source_lang], self.DECIMAL_SEPARATORS[self.target_lang])
            else:
                repaired_string_number = original_string_number.replace(
                    self.DECIMAL_SEPARATORS[self.target_lang], self.DECIMAL_SEPARATORS[self.source_lang])

            return sentence.replace(original_string_number, repaired_string_number)

        return None

    @staticmethod
    def __split_number_unit(text: str, decimal_separator: str) -> Tuple[Number, str]:
        """Split number-unit sentence part into separate variables.

        Number is parsed as a float or int. It uses language specific decimal separator.

        :param text: Part of the sentence to split.
        :param decimal_separator: Decimal separator to use.
        :return: Tuple with number and unit as it was split
        :rtype: tuple with number (float, int) and str
        """
        unit = None
        decimal = False

        # fix of situation: "Back in 1892, 250 kilometres"
        multiple_sentences_split = text.split(', ')
        if len(multiple_sentences_split) > 1:
            text = multiple_sentences_split[-1]

        number_string = []

        for idx, ch in enumerate(text):
            if ch.isdigit():
                number_string.append(ch)
            elif ch == decimal_separator:
                number_string.append('.')
                decimal = True
            elif ch.isalpha():
                unit = text[idx:].strip(' -')
                break

        if decimal:
            number = float("".join(number_string))
        else:
            number = int("".join(number_string))

        return number, unit

    @staticmethod
    def __get_string_number(text: str) -> str:
        """Returns number as a string (including decimal and thousands separator)"""
        # fix of situation: "Back in 1892, 250 kilometres"
        multiple_sentences_split = text.split(', ')
        if len(multiple_sentences_split) > 1:
            text = multiple_sentences_split[-1]

        for idx, char in enumerate(text):
            if str.isalpha(char):
                return text[:idx].strip()

    @staticmethod
    def __generate_translated_variants(number: int, rest: str, lang: str) -> List[str]:
        """Generates all possible variants (cartesian product) of number with unit.

        Actual supported patterns are:
          - 25cm
          - 25 cm
          - 25-cm

        :param number: Int or float number
        :param rest: Unit to be added to number
        :param lang: Language of unit
        :return: List of all variants
        :rtype: List of str
        """

        patterns = ["{}{}", "{} {}", "{}-{}"]

        numbers = [number, '{:,}'.format(number)]
        if lang == 'cs' and number in dt.en.keys():  # rewrite digit as a string
            numbers.append(dt.en[number])
        elif lang == 'en' and number in dt.cs.keys():
            numbers.append(dt.cs[number])

        rests = [rest] + _units.units[rest]

        variants = []

        for pat in patterns:
            for num in numbers:
                for res in rests:
                    variants.append(pat.format(num, res))

        return variants


