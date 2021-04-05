import re
from typing import Union, Optional, List, Tuple

from ._custom_types import Number
from ._languages import Language
from ._splitter import StringToNumberUnitConverter as Splitter
from ._statistics import StatisticsMarks
from ._units import units, Unit
from ._replacer import Replacer


class NumberFixer:
    """Fixer for problems with numbers and units.

    Checks whenever sentence contains any number-unit mistakes and tries to fix them. Based
    on count of number-unit pairs concrete fix methods are selected.

    For sentences where are more than one number-units pairs, the external tool (word-aligners)
    are used.

    :param: approximately: flag whenever it  should consider approximation phrases
    :param recalculate: flag whenever it should change correct units into different ones
    :param source_lang: language of the sentence given from user
    :param target_lang: language of the sentence translated by user
    """

    def __init__(self, approximately: bool, recalculate: bool, source_lang: Language, target_lang: Language):
        self.approximately = approximately
        self.recalculate = recalculate

        self.source_lang = source_lang
        self.target_lang = target_lang

        # preparing regex patterns based on supported units
        self.number_patter_source = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(source_lang)})\s?\d[\d .,]*|\d[\d .,]*[\s-]?(?:{units.get_regex_units_for_language(source_lang)})\b|\d+\'\d+\")")
        self.number_patter_target = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(target_lang)})\s?\d[\d .,]*|\d[\d .,]*[\s-]?(?:{units.get_regex_units_for_language(target_lang)})\b|\d+\'\d+\")")

    def fix_numbers_problems(self, original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Fix numbers problems in given sentence based on original text and translated text.

        There are two fixing methods. One for single number problem and the second for the rest. That is because
        there are used different heuristics for each case.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
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

    def __fix_sentence_multiple_units(self, numbers_units_pairs: List[Tuple[bool, Number, Unit]], original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Main method for fixing sentences with multiple number-unit pairs.

        Based on given filtered number-unit phrases it tries to verify
        whenever the translation contains same data. The translation
        is consider as correct if all the filtered phrases has matching
        phrases in the translation.

        :param numbers_units_pairs: filtered phrases with number-unit
        :param original_text: sentence in source language
        :param translated_text: original sentence translation
        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
        """
        problems_count = len(numbers_units_pairs)
        fixes_count = 0

        marks = [StatisticsMarks.MULTIPLE_NUMBER_UNIT_SENTENCE]

        for approximately, number, unit in numbers_units_pairs:
            single_fix, marks_individual = self.__fix_single_number((approximately, number, unit), original_text, translated_text)
            if single_fix is True:
                problems_count -= 1
                continue
            elif isinstance(single_fix, str):
                translated_text = single_fix
                fixes_count += 1
                problems_count -= 1
            marks += marks_individual

        if problems_count > 0:
            return False, list(dict.fromkeys(marks))
        elif fixes_count > 0:
            return translated_text, list(dict.fromkeys(marks))
        else:
            return True, [StatisticsMarks.MULTIPLE_NUMBER_UNIT_SENTENCE, StatisticsMarks.CORRECT_MULTIPLE_NUMBER_UNIT_SENTENCE]

    def __fix_single_number(self, problem_part: Tuple[bool, Number, Unit], original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Fix sentence with single number problem.

        It searches for matching number in both original and translated text and compares numbers and units.

        :param problem_part: extracted problematic part from the original sentence
        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
        """

        (approximately, number, unit) = problem_part

        marks = []

        # find all number-unit pairs in translated text
        translated_parts = re.findall(self.number_patter_target, translated_text)

        # uses when trying to decide where to replace wrong translation for the correct one
        best_part_fit = None

        # list of all same numbers with wrong unit, if the list contains just one item, the unit can be changed
        wrong_units = []

        # list of all wrong numbers with same unit, if the list contains just one item, the number can be changed
        wrong_number = []

        for translated_part in translated_parts:
            translated_part = translated_part.strip()
            tr_number, tr_unit = Splitter.split_number_unit(translated_part, self.target_lang)

            # same number, same unit
            if number == tr_number and unit.category == tr_unit.category:
                return True, [StatisticsMarks.CORRECT_NUMBER_UNIT]

            # same number, different unit
            elif number == tr_number and unit.category != tr_unit.category:
                wrong_units.append((tr_number, tr_unit, translated_part))
                '''
                suitable_unit = units.get_correct_unit(self.target_lang, number, unit, tr_unit)
                return translated_text.replace(tr_unit.word, suitable_unit.word), [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT]
                converted_number, new_unit = units.convert_number(self.target_lang, UnitsSystem.Imperial, number, unit, tr_unit)
                if isinstance(number, int):
                    converted_number = round(converted_number)
                else:
                    converted_number = round(converted_number, 2)
                return translated_text.replace(translated_part, f"{converted_number} {new_unit.word}")
                '''
            # different number, same unit
            elif number != tr_number and unit.category == tr_unit.category:
                wrong_number.append((tr_number, tr_unit, translated_part))

            # different number, different unit
            else:
                pass

        if len(wrong_units) == 1:
            tr_number, tr_unit, translated_part = wrong_units.pop()
            suitable_unit = units.get_correct_unit(self.target_lang, number, unit, tr_unit)
            fixed_sentence = Replacer.replace_unit(translated_text, translated_part, tr_number, tr_unit, suitable_unit)
            return fixed_sentence, [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT]

        if len(wrong_number) == 1:
            # TODO: Replacement
            pass

        return False, []

    def __find_numbers_units(self, text: str, language: Language) -> List[Tuple[bool, Number, Unit]]:
        """Search in sentence for number-unit parts

        When some part is found, it is divided into three parts - approximately (whenever the number is precise or not),
        number itself (parsed into int or float) and some unit from list.

        :param text: Sentence to search in.
        :param language: Language of the sentence
        :return: All found parts
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

            number, unit = Splitter.split_number_unit(part, language)

            problems.append((approximately, number, unit))

        return problems

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
