import re
from typing import List

from ._custom_types import *
from ._languages import Language
from ._splitter import StringToNumberUnitConverter as Splitter
from ._units import Unit


class NumberUnitFinderResult:

    def __init__(self, number: Number, unit: Unit, approximately: bool, text_part: str):
        self.number = number
        self.unit = unit
        self.approximately = approximately
        self.text_part = text_part
        self.scaling = None

    def add_scaling(self, scaling: int):
        self.scaling = scaling
        self.number *= scaling


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
