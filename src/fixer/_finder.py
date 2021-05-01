import re
from typing import List

from ._custom_types import *
from ._languages import Language
from ._splitter import StringToNumberUnitConverter as Splitter
from ._units import Unit, units
from ._lemmatization import UDPipeApi
from ._words_to_numbers_converter import WordsNumbersConverter

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
                pairs[-1].add_scaling(language.big_numbers_scale[scale_key])

        return pairs

    @staticmethod
    def find_word_number_unit(sentence: str, language: Language):
        #  Get lemmatization
        word_numbers = UDPipeApi.get_lemmatization(sentence, language, False)
        if not word_numbers:
            return []

        values = []
        current_phrase = []
        inside_number_phrase = False
        last_end = None

        #  Concantenate numbers as words together next to each other
        for data in word_numbers:
            if data['word'][0].isdigit():
                continue
            elif data['upostag'] != 'NUM' and data['lemma'] not in language.big_numbers_scale.keys() and not (data['upostag'] == 'PUNC' and inside_number_phrase):
                if current_phrase:
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
                values.append(current_phrase)
                current_phrase = [data]

            last_end = data['rangeEnd']

        if current_phrase:
            values.append(current_phrase)

        found_number_units = []

        #  Convert to number and found out unit
        for phrase in values:
            sentence_part = sentence[phrase[0]['rangeStart']:phrase[-1]['rangeEnd']]
            results = re.findall(rf"(({units.get_regex_units_for_language_before_numbers(language)})\s?{sentence_part})|[a-zA-Z,.][\s-]?({sentence_part}[\s-]?({units.get_regex_units_for_language(language)})\b)", sentence)
            for result in results:
                whole_match = result[0] if result[0] else result[2]

                # search for some approximately word before the number
                approximately = False
                if re.search(f"({'|'.join(language.approximately_phrases)}) {whole_match}", sentence):
                    approximately = True

                number = WordsNumbersConverter.convert([data['lemma'] for data in phrase if data['upostag'] != 'PUNC'], language)
                unit = result[1] if result[1] else result[3]

                found_number_units.append(NumberUnitFinderResult(number, units.get_unit_by_word(unit, language), approximately, whole_match))
                found_number_units[-1].set_number_as_string(sentence_part)

        return found_number_units
