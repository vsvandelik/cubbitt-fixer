import re
from typing import Union, List, Tuple, Dict

from ._decimal_separator_fixer import DecimalSeparatorFixer
from ._finder import Finder, NumberUnitFinderResult
from ._replacer import Replacer
from ._sentence_pair import SentencePair
from ._splitter import StringToNumberUnitConverter as Splitter
from ._statistics import StatisticsMarks
from ._units import units
from .fixer_configurator import FixerConfigurator, FixerModes


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
    """

    def __init__(self, configuration: FixerConfigurator):
        self.configuration = configuration

        self.source_lang = configuration.source_lang
        self.target_lang = configuration.target_lang

        # preparing regex patterns based on supported units
        self.number_patter_source = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(self.source_lang)})\s?\d([\d .,]*\d)?\s?(?:{self.source_lang.big_numbers_scale_keys})?|\d([\d .,]*\d)?[\s-]?((?:{self.source_lang.big_numbers_scale_keys})\s)?(?:{units.get_regex_units_for_language(self.source_lang)})\b|\d+\'\d+\")")
        self.number_patter_target = re.compile(
            rf"((?:{units.get_regex_units_for_language_before_numbers(self.target_lang)})\s?\d([\d .,]*\d)?\s?(?:{self.target_lang.big_numbers_scale_keys})?|\d([\d .,]*\d)?[\s-]?((?:{self.target_lang.big_numbers_scale_keys})\s)?(?:{units.get_regex_units_for_language(self.target_lang)})\b|\d+\'\d+\")")

    def fix(self, sentence_pair: SentencePair) -> Tuple[Union[str, bool], List]:
        """Fix numbers problems in given sentence based on original text and translated text.

        There are two fixing methods. One for single number problem and the second for the rest. That is because
        there are used different heuristics for each case.

        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
        """

        src_lang_numbers_units = Finder.find_number_unit_pairs(sentence_pair.source_text, self.source_lang, self.number_patter_source)
        trg_lang_numbers_units = Finder.find_number_unit_pairs(sentence_pair.target_text, self.target_lang, self.number_patter_target)

        marks = []

        if len(src_lang_numbers_units) == 0 and len(trg_lang_numbers_units) == 0:
            return True, []

        elif len(src_lang_numbers_units) != len(trg_lang_numbers_units):
            number_as_word_src = Finder.find_word_number_unit(sentence_pair.source_text, self.source_lang, sentence_pair.source_lemmas)
            if number_as_word_src:
                marks += [StatisticsMarks.NUMBER_AS_WORD]
                src_lang_numbers_units += number_as_word_src

            number_as_word_trg = Finder.find_word_number_unit(sentence_pair.target_text, self.target_lang, sentence_pair.target_lemmas)
            if number_as_word_trg:
                marks += [StatisticsMarks.NUMBER_AS_WORD]
                trg_lang_numbers_units += number_as_word_trg

            if len(src_lang_numbers_units) != len(trg_lang_numbers_units):
                marks += [StatisticsMarks.UNFIXABLE_PART]

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

        result_sentence = sentence_pair.target_text

        for idx, val in levels.items():
            binding = self.__process_src_trg_pairs_relationships(relationships, idx)
            result_sentence, m = val(binding, src_lang_numbers_units, trg_lang_numbers_units, result_sentence)
            marks += m

        if result_sentence == sentence_pair.target_text:
            return True, marks
        else:
            return result_sentence, marks

    def __process_sentence_same_number_same_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        if self.configuration.mode == FixerModes.FIXING:
            return sentence, [StatisticsMarks.CORRECT_NUMBER_UNIT] if len(bindings) else []

        for binding_trg, binding_src in bindings:
            src_pair = src_lang_numbers_units[binding_src]
            trg_pair = trg_lang_numbers_units[binding_trg]
            if trg_pair.unit.category.system in self.configuration.target_units:
                continue
            converted_number, converted_unit = units.convert_number(self.target_lang, self.configuration.target_units, src_pair.number, src_pair.unit, trg_pair.unit)
            if not converted_unit or not converted_unit:
                return sentence, [StatisticsMarks.UNABLE_TO_RECALCULATE]
            sentence = Replacer.replace_unit_number(sentence, trg_pair, src_pair.number, converted_number, converted_unit, self.target_lang)

        return sentence, [StatisticsMarks.RECALCULATED] if len(bindings) else []

    def __process_sentence_same_number_different_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        for binding_trg, binding_src in bindings:
            src_pair = src_lang_numbers_units[binding_src]
            trg_pair = trg_lang_numbers_units[binding_trg]

            if self.configuration.mode == FixerModes.FIXING:
                suitable_unit = units.get_correct_unit(self.target_lang, src_pair.number, src_pair.unit, trg_pair.unit)
                sentence = Replacer.replace_unit(sentence, trg_pair.text_part, trg_pair.number, trg_pair.unit, suitable_unit)
            else:
                converted_number, converted_unit = units.convert_number(self.target_lang, self.configuration.target_units, src_pair.number, src_pair.unit, trg_pair.unit)
                if converted_unit and converted_unit:
                    sentence = Replacer.replace_unit_number(sentence, trg_pair, src_pair.number, converted_number, converted_unit, self.target_lang)

        return sentence, [StatisticsMarks.CORRECT_NUMBER_WRONG_UNIT] if len(bindings) else []

    def __process_sentence_different_number_same_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        change = False
        tolerance_marks = []

        for binding_trg, binding_src in bindings:
            src_pair = src_lang_numbers_units[binding_src]
            trg_pair = trg_lang_numbers_units[binding_trg]

            if self.configuration.mode == FixerModes.RECALCULATING:
                converted_number, converted_unit = units.convert_number(self.target_lang, self.configuration.target_units, src_pair.number, src_pair.unit, trg_pair.unit)
                if converted_unit and converted_unit:
                    sentence = Replacer.replace_unit_number(sentence, trg_pair, src_pair.number, converted_number, converted_unit, self.target_lang)
                    change = True
            else:

                if self.__consider_tolerance_rates(src_pair, trg_pair):
                    tolerance_marks = [StatisticsMarks.APPLIED_TOLERANCE_RATE]
                    continue

                src_number = str(src_pair.number) if src_pair.number_as_string else Splitter.extract_string_number_from_number_unit_string(src_pair.text_part)

                idx_dec_sep = src_number.find(self.source_lang.decimal_separator)
                idx_ths_sep = src_number.find(self.source_lang.thousands_separator)
                if -1 < idx_dec_sep < idx_ths_sep and idx_ths_sep > -1:
                    continue

                # TODO: How about numbers with scaling?

                trg_number = trg_pair.number_as_string if trg_pair.number_as_string else trg_pair.text_part.replace(trg_pair.unit.word, '').strip()

                swapped_separators = DecimalSeparatorFixer.swap_separators(src_number)
                sentence = Replacer.replace_number(sentence, trg_pair.text_part, trg_number, swapped_separators)
                change = True

        return sentence, ([StatisticsMarks.WRONG_NUMBER_CORRECT_UNIT] if len(bindings) and change else []) + tolerance_marks

    def __process_sentence_different_number_different_unit(self, bindings: List[Tuple[int, int]], src_lang_numbers_units: List[NumberUnitFinderResult], trg_lang_numbers_units: List[NumberUnitFinderResult], sentence: str) -> Tuple[str, list]:
        tolerance_marks = []

        for binding_trg, binding_src in bindings:
            src_pair = src_lang_numbers_units[binding_src]
            trg_pair = trg_lang_numbers_units[binding_trg]

            if self.configuration.mode == FixerModes.RECALCULATING:
                converted_number, converted_unit = units.convert_number(self.target_lang, self.configuration.target_units, src_pair.number, src_pair.unit, trg_pair.unit)
                if converted_unit and converted_unit:
                    sentence = Replacer.replace_unit_number(sentence, trg_pair, src_pair.number, converted_number, converted_unit, self.target_lang)
            else:
                if self.__consider_tolerance_rates(src_pair, trg_pair):
                    tolerance_marks = [StatisticsMarks.APPLIED_TOLERANCE_RATE]
                    continue

                suitable_unit = units.get_correct_unit(self.target_lang, src_pair.number, src_pair.unit, trg_pair.unit)
                sentence = Replacer.replace_unit_number(sentence, trg_pair, src_pair.number, src_pair.number, suitable_unit, self.target_lang)

        return sentence, ([StatisticsMarks.WRONG_NUMBER_UNIT] if len(bindings) else []) + tolerance_marks

    def __consider_tolerance_rates(self, src_pair, trg_pair):
        base_src_number = units.convert_to_base_in_category(src_pair.unit, src_pair.number)
        converted_trg_number = units.convert_to_base_in_another_system(trg_pair.unit, trg_pair.number, src_pair.unit.category)

        if src_pair.approximately:
            tolerance = base_src_number * self.configuration.approximately_tolerance
        else:
            tolerance = base_src_number * self.configuration.base_tolerance

        if not converted_trg_number:
            return False

        if (base_src_number - tolerance) < converted_trg_number < (base_src_number + tolerance):
            return True

        return False

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

        if len(relationships) and level == 3:
            return results

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
