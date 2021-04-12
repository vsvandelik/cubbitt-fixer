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

            # search for some approximately word before the number
            approximately = False
            if re.search(f"({'|'.join(language.approximately_phrases)}) {part}", sentence):
                approximately = True

            number, unit = Splitter.split_number_unit(part, language)

            pairs.append(NumberUnitFinderResult(number, unit, approximately, part))

        return pairs
