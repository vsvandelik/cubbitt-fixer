import argparse
import re
from typing import Union, Optional, List, Tuple

from ._alignerapi import AlignerApi
from ._languages import Languages, Language
from ._units import units, Unit
from ._statistics import StatisticsMarks

Number = Union[int, float]


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
        repair = self.numbers_fixer.fix_numbers_problems(original_text, translated_text)

        return repair


class NumberFixer:
    """Fixer for problems with numbers with units.

    Checks whenever sentence contains any number-unit mistakes and tries to fix them.
    Currently it supports fixing sentences where is only one number-unit pair.

    Currently implemented fixes:

    - untranslated decimal points marks
    - replacing wrong units for their original variants
    """

    def __init__(self, approximately: bool, recalculate: bool, source_lang: Language, target_lang: Language):
        self.approximately = approximately
        self.recalculate = recalculate

        self.source_lang = source_lang
        self.target_lang = target_lang

        # preparing regex patterns based on supported units
        self.number_patter_source = re.compile(rf"(\d[\d .,]*[\s-]?(?:{units.get_regex_units_for_language(source_lang)})\b|\d+\'\d+\")")
        self.number_patter_target = re.compile(rf"(\d[\d .,]*[\s-]?(?:{units.get_regex_units_for_language(target_lang)})\b|\d+\'\d+\")")

    def fix_numbers_problems(self, original_text: str, translated_text: str) -> Tuple[Optional[Union[str, bool]], List]:
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
        problems = self.__find_numbers_units(original_text, self.source_lang)

        if len(problems) == 1:
            fix_result, marks = self.__fix_single_number(problems[0], original_text, translated_text)
            marks.append(StatisticsMarks.SINGLE_NUMBER_UNIT_SENTENCE)
            return fix_result, marks
        elif len(problems) > 1:
            return self.__fix_sentence_multiple_units(problems, original_text, translated_text)
        else:
            return True, []

    def __fix_sentence_multiple_units(self, numbers_units_pairs: List[Tuple[bool, Number, Unit]], original_text: str, translated_text: str):
        if self.source_lang == Languages.CS:
            word_alignment = AlignerApi.get_alignment(translated_text, original_text)
        else:
            word_alignment = AlignerApi.get_alignment(original_text, translated_text)

        problems_count = len(numbers_units_pairs)

        for approximately, number, unit in numbers_units_pairs:
            single_fix, _ = self.__fix_single_number((approximately, number, unit), original_text, translated_text)
            if single_fix is True:
                problems_count -= 1
                continue

        if problems_count > 0:
            return False, [StatisticsMarks.MULTIPLE_NUMBER_UNIT_SENTENCE]
        else:
            return True, [StatisticsMarks.MULTIPLE_NUMBER_UNIT_SENTENCE, StatisticsMarks.CORRECT_MULTIPLE_NUMBER_UNIT_SENTENCE]

    def __fix_single_number(self, problem_part: Tuple[bool, Number, Unit], original_text: str, translated_text: str) -> Tuple[Optional[Union[str, bool]],List]:
        """Fix sentence with single number problem.

        It searches for matching number in both original and translated text and compares numbers and units.

        :param problem_part: extracted problematic part from the original sentence
        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: repaired sentence or True when sentence is correct or False when sentence cannot be fixed
        :rtype: str or boolean
        """

        (approximately, number, unit) = problem_part

        marks = []

        # find all number-unit pairs in translated text
        translated_parts = re.findall(self.number_patter_target, translated_text)

        # uses when trying to decide where to replace wrong translation for the correct one
        best_part_fit = None

        for translated_part in translated_parts:
            tr_number, tr_unit = self.__split_number_unit(translated_part, self.target_lang)

            # same number, same unit
            if number == tr_number and unit.category == tr_unit.category:
                return True, [StatisticsMarks.CORRECT_NUMBER_UNIT]

            # same number, different unit
            elif number == tr_number and unit.category != tr_unit.category:
                suitable_unit = units.get_correct_unit(self.target_lang, number, unit, tr_unit)
                return translated_text.replace(tr_unit.word, suitable_unit.word), [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT]
                '''
                converted_number, new_unit = units.convert_number(self.target_lang, UnitsSystem.Imperial, number, unit, tr_unit)
                if isinstance(number, int):
                    converted_number = round(converted_number)
                else:
                    converted_number = round(converted_number, 2)
                return translated_text.replace(translated_part, f"{converted_number} {new_unit.word}")
                '''
            # different number, same unit
            elif number != tr_number and unit.category == tr_unit.category:

                # verifies if the problem is caused by untranslated decimal separator
                problem_with_separator = self.__fix_wrong_decimal_separator(number, tr_number, translated_part, translated_text)
                if problem_with_separator:
                    return problem_with_separator, [StatisticsMarks.DECIMAL_SEPARATOR_PROBLEM]

                best_part_fit = translated_part

            # different number, different unit
            elif not best_part_fit:
                best_part_fit = translated_part

        if best_part_fit:
            return translated_text.replace(best_part_fit, f"{number} {units.get_correct_unit(self.target_lang, number, unit).word}"), []

        return False, []

    def __find_numbers_units(self, text: str, language: Language) -> List[Tuple[bool, Number, Unit]]:
        """Search in sentence for number-unit parts

        When some part is found, it is divided into three parts - approximately (whenever the number is precise or not),
        number itself (parsed into int or float) and some unit from list.

        :param text: Sentence to search in.
        :param language: Language of the sentence
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
            if re.search(f"({'|'.join(language.approximately_phrases)}) {part}", text):
                approximately = True

            number, unit = self.__split_number_unit(part, language)

            problems.append((approximately, number, unit))

        return problems

    def __fix_wrong_decimal_separator(self, number_original: Number, number_translated: Number, number_unit_translated: str, sentence: str) -> Optional[str]:
        """Verifies if the problem with number is decimal-separator-based and tries to fix it.

        :param number_original: number extracted from original sentence
        :param number_translated: number extracted from translated sentence
        :param number_unit_translated: number-unit part from translated sentence
        :param sentence: full translated sentence
        :return: repaired sentence or None when the sentence is correct
        :rtype: str or None when the sentence does not have problem
        """

        # tries to split number with opposite decimal separator
        tr_number_another_separator, _ = self.__split_number_unit(number_unit_translated, self.target_lang, custom_separator=self.target_lang.thousands_separator)

        if number_original == tr_number_another_separator:
            original_string_number = self.__get_string_number(number_unit_translated)

            if isinstance(number_original, int):
                repaired_string_number = original_string_number.replace(self.source_lang.thousands_separator, self.target_lang.thousands_separator)
            else:
                repaired_string_number = original_string_number.replace(self.source_lang.decimal_separator, self.target_lang.decimal_separator)

            return sentence.replace(original_string_number, repaired_string_number)

        return None

    @staticmethod
    def __split_number_unit(text: str, language: Language, *, custom_separator: str = None) -> Tuple[Number, Unit]:
        """Split number-unit sentence part into separate variables.

        Number is parsed as a float or int. It uses language specific decimal separator.

        :param text: Part of the sentence to split.
        :param language: Language of the text
        :param custom_separator: Keyword-only parameter for specifying custom decimal separator
        :return: Tuple with number and unit as it was split
        :rtype: tuple with number (float, int) and str
        """
        unit = None
        decimal = False

        if not custom_separator:
            custom_separator = language.decimal_separator

        if '"' in text or "'" in text:
            return NumberFixer.__convert_text_to_inches(text), units.get_unit_by_word('inch', language)

        # fix of situation: "Back in 1892, 250 kilometres"
        multiple_sentences_split = text.split(', ')
        if len(multiple_sentences_split) > 1:
            text = multiple_sentences_split[-1]

        number_string = []

        for idx, ch in enumerate(text):
            if ch.isdigit():
                number_string.append(ch)
            elif ch == custom_separator:
                number_string.append('.')
                decimal = True
            elif ch.isalpha():
                unit = text[idx:].strip(' -')
                break

        if decimal:
            number = float("".join(number_string))
        else:
            number = int("".join(number_string))

        unit = units.get_unit_by_word(unit, language)

        return number, unit

    @staticmethod
    def __convert_text_to_inches(text: str):
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
