import re
from typing import Union, List, Tuple, Dict

from ._finder import Finder, NumberUnitFinderResult
from ._languages import Language
from ._replacer import Replacer
from ._statistics import StatisticsMarks
from ._units import units


class Relationship:

    def __init__(self):
        self.same_number_same_unit = set()
        self.same_number_different_unit = set()
        self.different_number_same_unit = set()
        self.different_number_different_unit = set()

    def remove_src_sentence(self, idx: int):
        self.same_number_same_unit.discard(idx)
        self.same_number_different_unit.discard(idx)
        self.different_number_same_unit.discard(idx)
        self.different_number_different_unit.discard(idx)

    def get_list_by_level(self, level: int):
        levels = {
            0: self.same_number_same_unit,
            1: self.same_number_different_unit,
            2: self.different_number_same_unit,
            3: self.different_number_different_unit
        }
        return levels[level]


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

    def __init__(self, approximately: bool, recalculate: bool, source_lang: Language, target_lang: Language, normal_inaccuracy: float, approximately_inaccuracy: float):
        self.approximately = approximately
        self.recalculate = recalculate

        self.source_lang = source_lang
        self.target_lang = target_lang

        # preparing regex patterns based on supported units
        self.number_patter_source = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(source_lang)})\s?\d[\d .,]*(\s(?:{source_lang.big_numbers_scale_keys}))?|\d[\d .,]*[\s-]?((?:{source_lang.big_numbers_scale_keys})\s)?(?:{units.get_regex_units_for_language(source_lang)})\b|\d+\'\d+\")")
        self.number_patter_target = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(target_lang)})\s?\d[\d .,]*(\s(?:{target_lang.big_numbers_scale_keys}))?|\d[\d .,]*[\s-]?((?:{target_lang.big_numbers_scale_keys})\s)?(?:{units.get_regex_units_for_language(target_lang)})\b|\d+\'\d+\")")

        self.normal_inaccuracy = normal_inaccuracy
        self.approximately_inaccuracy_inaccuracy = approximately_inaccuracy

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

        src_lang_numbers_units = Finder.find_number_unit_pairs(original_text, self.source_lang, self.number_patter_source)
        trg_lang_numbers_units = Finder.find_number_unit_pairs(translated_text, self.target_lang, self.number_patter_target)

        marks = []

        if len(src_lang_numbers_units) == 0 and len(trg_lang_numbers_units) == 0:
            return True, []

        elif len(src_lang_numbers_units) != len(trg_lang_numbers_units):
            return False, [StatisticsMarks.DIFFERENT_COUNT_NUMBERS_UNITS]

        elif len(src_lang_numbers_units) == 1 and len(trg_lang_numbers_units) == 1:
            marks.append(StatisticsMarks.SINGLE_NUMBER_UNIT_SENTENCE)

        else:
            marks.append(StatisticsMarks.MULTIPLE_NUMBER_UNIT_SENTENCE)

        relationships = self.__prepare_src_trg_pairs_relationships(src_lang_numbers_units, trg_lang_numbers_units)

        levels = {
            0: self.__process_sentence_same_number_same_unit,
            1: self.__process_sentence_same_number_different_unit,
            2: self.__process_sentence_different_number_same_unit,
            3: self.__process_sentence_different_number_different_unit,
        }

        result_sentence = translated_text

        for idx, val in levels.items():
            binding = self.__process_src_trg_pairs_relationships(relationships, idx)
            result_sentence, m = val(binding, src_lang_numbers_units, trg_lang_numbers_units, result_sentence)
            marks += m

        if result_sentence == translated_text:
            return True, marks
        else:
            return result_sentence, marks

    def __process_sentence_same_number_same_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        return sentence, [StatisticsMarks.CORRECT_NUMBER_UNIT] if len(bindings) else []

    def __process_sentence_same_number_different_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        for binding_trg, binding_src in bindings:
            src_pair = src_lang_numbers_units[binding_src]
            trg_pair = trg_lang_numbers_units[binding_trg]
            suitable_unit = units.get_correct_unit(self.target_lang, src_pair.number, src_pair.unit, trg_pair.unit)
            sentence = Replacer.replace_unit(sentence, trg_pair.text_part, trg_pair.number, trg_pair.unit, suitable_unit)

        return sentence, [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT] if len(bindings) else []

    def __process_sentence_different_number_same_unit(
            self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        return sentence, [StatisticsMarks.WRONG_NUMBER_CORRECT_UNIT] if len(bindings) else []

    def __process_sentence_different_number_different_unit(
            self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        return sentence, [StatisticsMarks.WRONG_NUMBER_UNIT] if len(bindings) else []

    @staticmethod
    def __process_src_trg_pairs_relationships(relationships: Dict[int, Relationship], level: int) -> List[Tuple[int, int]]:
        results = []

        while len(relationships):
            some_change = False
            to_remove = []

            for trg_idx, target_sentence in relationships.items():
                if len(target_sentence.get_list_by_level(level)) == 1:
                    idx = target_sentence.get_list_by_level(level).pop()
                    to_remove.append(trg_idx)
                    results.append((trg_idx, idx))
                    some_change = True
                    [o.remove_src_sentence(idx) for _, o in relationships.items()]

            [relationships.pop(idx) for idx in to_remove]

            if not some_change:
                break

        to_remove = []
        for trg_idx, target_sentence in relationships.items():
            if len(target_sentence.get_list_by_level(level)):
                idx = target_sentence.get_list_by_level(level).pop()
                to_remove.append(trg_idx)
                results.append((trg_idx, idx))
                [o.remove_src_sentence(idx) for _, o in relationships.items()]
        [relationships.pop(idx) for idx in to_remove]

        return results

    @staticmethod
    def __prepare_src_trg_pairs_relationships(src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult]) -> Dict[int, Relationship]:
        relationships = {}

        for trg_idx, trg_pair in enumerate(trg_lang_numbers_units):

            relationship = Relationship()

            for idx, src_pair in enumerate(src_lang_numbers_units):

                # same number, same unit
                if src_pair.number == trg_pair.number and src_pair.unit.category == trg_pair.unit.category:
                    relationship.same_number_same_unit.add(idx)

                # same number, different unit
                elif src_pair.number == trg_pair.number and src_pair.unit.category != trg_pair.unit.category:
                    relationship.same_number_different_unit.add(idx)

                # different number, same unit
                elif src_pair.number != trg_pair.number and src_pair.unit.category == trg_pair.unit.category:
                    relationship.different_number_same_unit.add(idx)

                # different number, different unit
                else:
                    relationship.different_number_different_unit.add(idx)

            relationships[trg_idx] = relationship

        return relationships


'''
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
                
                suitable_unit = units.get_correct_unit(self.target_lang, number, unit, tr_unit)
                return translated_text.replace(tr_unit.word, suitable_unit.word), [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT]
                converted_number, new_unit = units.convert_number(self.target_lang, UnitsSystem.Imperial, number, unit, tr_unit)
                if isinstance(number, int):
                    converted_number = round(converted_number)
                else:
                    converted_number = round(converted_number, 2)
                return translated_text.replace(translated_part, f"{converted_number} {new_unit.word}")
              
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
'''
