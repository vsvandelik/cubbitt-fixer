import re
from typing import List

from fixer._words_to_numbers_converter import WordsNumbersConverter

from ._custom_types import *
from ._languages import Language, Languages
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
        self.modifier = False

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
            part = part[0].strip(" .,-")

            # search for some approximately word before the number
            approximately = False
            if re.search(rf"({'|'.join(language.approximately_phrases)}) {part}", sentence):
                approximately = True

            part_without_scaling = part
            scale_key = None
            for scale in language.big_numbers_scale:
                if re.search(rf"(\b|[0-9]){scale}((?!\w)|$)", part):
                    scale_key = scale
                    part_without_scaling = part.replace(scale, '').strip(" -,.")
                    break

            millions = False
            if scale_key is None and re.search(r"\d[ ,.\d]*m(?!\w)", part) and re.sub(r"\d[ ,.\d]*m(?!\w)", "", part, re.UNICODE).strip() != "":
                part_without_scaling = re.sub(r"([^a-zA-Z])m([^a-zA-Z]|$)", r"\1 \2", part).strip()
                millions = True

            number, unit = Splitter.split_number_unit(part_without_scaling, language)

            pairs.append(NumberUnitFinderResult(number, unit, approximately, part))

            if '-' in part:
                pairs[-1].modifier = True

            if scale_key:
                pairs[-1].add_scaling(language.big_numbers_scale[scale_key][0])
            elif millions:
                pairs[-1].add_scaling(1000000)

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
            if data['upostag'] != 'NUM' and \
                    data['lemma'] not in language.big_numbers_scale.keys() and \
                    not (data['upostag'] == 'PUNCT' and inside_number_phrase) and \
                    not (data['word'] == 'and' and language.acronym == Languages.EN.acronym and inside_number_phrase) and \
                    not (data['word'] == 'a' and language.acronym == Languages.CS.acronym and inside_number_phrase):
                if current_phrase:
                    if current_phrase[-1]['upostag'] == 'PUNCT':
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
                if current_phrase[-1]['upostag'] == 'PUNCT':
                    current_phrase.pop()
                values.append(current_phrase)
                current_phrase = [data]

            last_end = data['rangeEnd']

        if current_phrase:
            if current_phrase[-1]['upostag'] == 'PUNCT':
                current_phrase.pop()
            values.append(current_phrase)

        found_number_units = []

        for phrase in values:
            if all(word['upostag'] == 'PUNCT' or word['word'][0].isdigit() for word in phrase):
                continue
            # if len(phrase) == 1 and phrase[0]['word'][0].isdigit():
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

            # search for scaling word
            scaling_words = [word['word'] for word in phrase if word['word'] in language.big_numbers_scale]
            scaling_word = None
            if scaling_words:
                scaling_word = scaling_words[0]

            number = WordsNumbersConverter.convert([data['lemma'] for data in phrase if data['upostag'] != 'PUNCT'], language)

            found_number_units.append(NumberUnitFinderResult(number, units.get_unit_by_word(matched_unit, language), approximately, whole_match))
            found_number_units[-1].set_number_as_string(sentence[start:end + 1].strip(" -"))

            if '-' in whole_match:
                found_number_units[-1].modifier = True

            if scaling_word:
                found_number_units[-1].scaling = language.big_numbers_scale[scaling_word][0]

        return found_number_units
