from ._languages import Languages, Language
from ._custom_types import *
from typing import List, Dict, Tuple

from word2number import w2n

class WordsNumbersConverter:

    __CS = {
        'nula': 0,
        'jedna': 1,
        'dva': 2,
        'dvě': 2,
        'tři': 3,
        'čtyři': 4,
        'pět': 5,
        'šest': 6,
        'sedm': 7,
        'osm': 8,
        'devět': 9,
        'deset': 10,
        'jedenáct': 11,
        'dvanáct': 12,
        'třináct': 13,
        'čtrnáct': 14,
        'patnáct': 15,
        'šestnáct': 16,
        'sedmnáct': 17,
        'osmnáct': 18,
        'devatenáct': 19,
        'dvacet': 20,
        'třicet': 30,
        'čtyřice': 40,
        'padesát': 50,
        'šedesát': 60,
        'sedmdesát': 70,
        'osmdesát': 80,
        'devadesát': 90,
    }

    @staticmethod
    def convert(phrase: str, language: Language) -> Number:
        if language == Languages.CS:
            return WordsNumbersConverter.__cz_converter(phrase)
        elif language == Languages.EN:
            return WordsNumbersConverter.__en_converter(phrase)

        return None

    @staticmethod
    def __cz_converter(phrase: List[str]) -> Number:
        sum = 0

        last_number = 0
        for word in phrase:
            if word in WordsNumbersConverter.__CS.keys():
                last_number += WordsNumbersConverter.__CS[word]
            elif word in Languages.CS.big_numbers_scale.keys():
                if last_number == 0:
                    sum += Languages.CS.big_numbers_scale[word]
                else:
                    sum += last_number * Languages.CS.big_numbers_scale[word]
                last_number = 0

        if last_number > 0:
            sum += last_number

        return sum

    @staticmethod
    def __en_converter(phrase: List[str]) -> Number:
        return w2n.word_to_num(" ".join(phrase))

if __name__ == "__main__":
    print(WordsNumbersConverter.convert(["two", "million", "three", "thousand", "nine", "hundred", "and", "eighty", "four"], Languages.EN))