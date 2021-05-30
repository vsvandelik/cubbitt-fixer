import re
from typing import List

from fixer._words_to_numbers_converter import WordsNumbersConverter

from ._custom_types import *
from ._languages import Language
from ._splitter import StringToNumberUnitConverter as Splitter
from ._units import Unit, units


class NumberUnitFinderResult:

    def __init__(self, number: Number, unit: Unit, approximately: bool, text_part: str):
        self.number = number
        self.unit = unit
        self.approximately = approximately
        self.text_part = text_part
        self.scaling = None
        self.number_as_string = None

    def add_scaling(self, scaling: int):
        self.scaling = scaling
        self.number *= scaling

    def set_number_as_string(self, word_number):
        self.number_as_string = word_number


class TextNumberPhrase:

    def __init__(self):
        self.unit = None
        self.unit_before_number = None
        self.number_parts = []


class Finder:

    @staticmethod
    def find_number_unit_pairs(sentence: str, language: Language, pattern: re.Pattern) -> List[NumberUnitFinderResult]:
        """Search in sentence for number-unit parts

        Based on regular expression the pairs of numbers and units are
        searched within the input sentence. Also the approximately
        phrases are searched.

        :param sentence: Sentence to search in
        :param language: Language of the sentence
        :param pattern: Regular expression patter with the units, etc.
        :return: List of found pairs
        """
        parts = re.findall(pattern, sentence)
        if len(parts) == 0:  # any number-digit part in original text
            return []

        pairs = []
        for part in parts:
            part = part[0]

            # search for some approximately word before the number
            approximately = False
            if re.search(f"({'|'.join(language.approximately_phrases)}) {part}", sentence):
                approximately = True

            part_without_scaling = part
            scale_key = None
            for scale in language.big_numbers_scale.keys():
                if scale in part:
                    scale_key = scale
                    part_without_scaling = part.replace(scale, '')
                    break

            number, unit = Splitter.split_number_unit(part_without_scaling, language)

            pairs.append(NumberUnitFinderResult(number, unit, approximately, part))

            if scale_key:
                pairs[-1].add_scaling(language.big_numbers_scale[scale_key][0])

        return pairs

    @staticmethod
    def find_word_number_unit(sentence: str, language: Language, lemmatization):
        #  Get lemmatization
        if not lemmatization or not any(word['upostag'] == 'NUM' and not word['word'][0].isdigit() for word in lemmatization):
            return []

        values = []
        current_phrase = []
        inside_number_phrase = False
        last_end = None

        #  Concatenate numbers as words together next to each other
        for data in lemmatization:
            if data['upostag'] != 'NUM' and data['lemma'] not in language.big_numbers_scale.keys() and not (data['upostag'] == 'PUNC' and inside_number_phrase):
                if current_phrase:
                    if current_phrase[-1]['upostag'] == 'PUNC':
                        current_phrase.pop()
                    values.append(current_phrase)
                    current_phrase = []
                inside_number_phrase = False
                continue

            inside_number_phrase = True

            if not current_phrase:
                current_phrase.append(data)
            elif data['rangeStart'] <= last_end + 1:
                current_phrase.append(data)
            else:
                if current_phrase[-1]['upostag'] == 'PUNC':
                    current_phrase.pop()
                values.append(current_phrase)
                current_phrase = [data]

            last_end = data['rangeEnd']

        if current_phrase:
            if current_phrase[-1]['upostag'] == 'PUNC':
                current_phrase.pop()
            values.append(current_phrase)

        found_number_units = []

        for phrase in values:
            if all(word['upostag'] == 'PUNC' or word['word'][0].isdigit() for word in phrase):
                continue
            #if len(phrase) == 1 and phrase[0]['word'][0].isdigit():
            #    continue
            elif phrase[0]['word'][0].isdigit() and phrase[1]['word'] in language.big_numbers_scale.keys():
                continue

            start = phrase[0]['rangeStart']
            end = phrase[-1]['rangeEnd']
            matched_unit = None
            whole_match = None
            for unit in re.finditer(rf"\b({units.get_regex_units_for_language(language)})\b", sentence):
                if unit.group(0).strip() in units.get_regex_units_for_language_before_numbers_list(language) and 0 <= (start - unit.end()) <= 2:
                    matched_unit = unit.group(0)
                    whole_match = sentence[unit.start():end]
                    break
                elif 0 <= (unit.start() - end) <= 2:
                    matched_unit = unit.group(0)
                    whole_match = sentence[start:unit.end()]
                    break

            if not matched_unit:
                continue

            # search for some approximately word before the number
            approximately = False
            if re.search(f"({'|'.join(language.approximately_phrases)}) {whole_match}", sentence):
                approximately = True

            number = WordsNumbersConverter.convert([data['lemma'] for data in phrase if data['upostag'] != 'PUNC'], language)

            found_number_units.append(NumberUnitFinderResult(number, units.get_unit_by_word(matched_unit, language), approximately, whole_match))
            found_number_units[-1].set_number_as_string(sentence[start:end + 1])

        return found_number_units
