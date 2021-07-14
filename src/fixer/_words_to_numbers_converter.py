import re
from typing import List, Optional

from word2number import w2n

from ._custom_types import *
from ._languages import Languages, Language


class WordsNumbersConverterException(Exception):
    """Exception thrown when the text representation of the number cannot be converted."""
    pass


class WordsNumbersConverter:
    """Class for converting text representation of numbers into their digits representation

    For czech language it uses custom converting algorithms, which should be enable
    to convert numbers even in form of "petadvacet".

    For english it uses external package distributed via PyPI.
    """

    #: Text numbers table for czech language
    __CS = {
        'nula': 0,
        'jedna': 1,
        'jeden': 1,
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
        'čtyřicet': 40,
        'padesát': 50,
        'šedesát': 60,
        'sedmdesát': 70,
        'osmdesát': 80,
        'devadesát': 90,
    }

    #: Text numbers table for english language
    __EN = {
        'zero': 0,
        'null': 0,
        # 'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90
    }

    #: Regular expression pattern to search any number in string (czech)
    __CS_words_regex = re.compile(r"\b(" + "|".join(__CS.keys()) + r")\b", re.IGNORECASE)

    #: Regular expression pattern to search any number in string (english)
    __EN_words_regex = re.compile(r"\b(" + "|".join(__EN.keys()) + r")\b", re.IGNORECASE)

    @staticmethod
    def contains_text_numbers(sentence: str, language: Language) -> bool:
        """Verifies whenever the sentence contains any text-represented number

        It searches via regex for any word which should be indicating
        there is some number. It does not check any validity of the number.

        :param sentence: Sentence to search number in
        :param language: Language of the sentence
        :return: Bool whenever it contains any number
        """
        if language == Languages.CS and WordsNumbersConverter.__CS_words_regex.search(sentence):
            return True
        elif language == Languages.EN and WordsNumbersConverter.__EN_words_regex.search(sentence):
            return True

        return False

    @staticmethod
    def convert(phrase: List[str], language: Language) -> Optional[Number]:
        """Convert text-represented numbers into digits

        Based on list of words on input it construct one number
        which should be digits representation of those words.

        For czech it uses custom algorithm, for english external package is called.

        Supports only integers.

        :param phrase: List of words with numbers as text
        :param language: Language of the phrase words
        :return: Number if conversion was successful, None otherwise
        """
        if language == Languages.CS:
            return WordsNumbersConverter.__cz_converter(phrase)
        elif language == Languages.EN:
            return WordsNumbersConverter.__en_converter(phrase)

        return None

    @staticmethod
    def __cz_converter(phrase: List[str]) -> Number:
        """Converts czech words into single number"""
        sum = 0

        scaling = [Languages.CS.big_numbers_scale[word][0] for word in phrase if word in Languages.CS.big_numbers_scale.keys()]

        last_number = 0
        previous_was_scaling = False
        for word in phrase:

            if WordsNumbersConverter.__czech_shortcuts(word):  # format "pětadvacet"
                last_number += WordsNumbersConverter.__czech_shortcuts(word)
                previous_was_scaling = False

            elif word in WordsNumbersConverter.__CS.keys():
                last_number += WordsNumbersConverter.__CS[word]
                previous_was_scaling = False

            elif word in Languages.CS.big_numbers_scale.keys():
                actual_scaling = scaling.pop(0)

                if previous_was_scaling and last_number > 0:
                    last_number *= Languages.CS.big_numbers_scale[word][0]

                elif last_number == 0:
                    last_number = Languages.CS.big_numbers_scale[word][0]

                else:
                    last_number = last_number * Languages.CS.big_numbers_scale[word][0]

                if scaling and actual_scaling >= max(scaling):
                    sum += last_number
                    last_number = 0

                previous_was_scaling = True

            else:
                raise WordsNumbersConverterException("invalid word to convert")

        if last_number > 0:
            sum += last_number

        return sum

    @staticmethod
    def __czech_shortcuts(phrase: str) -> Number:
        """Converts number as 'pětadvacet' into digits"""
        parts = re.search(r"(jedn|dva|tři|čtyři|pět|šest|sedm|osm|devět)a(dvacet|třicet|čtyřicet|padesát|šedesát|sedmdesát|osmdesát|devadesát)", phrase, re.IGNORECASE)
        if not parts:
            return False

        return WordsNumbersConverter.__CS[parts.group(2)] + WordsNumbersConverter.__CS[parts.group(1) if parts.group(1) != "jedn" else "jedna"]

    @staticmethod
    def __en_converter(phrase: List[str]) -> Number:
        """Convers english phrase using w2n package"""
        if len(phrase) == 1 and phrase[0] in Languages.EN.big_numbers_scale:
            return Languages.EN.big_numbers_scale[phrase[0]][0]
        return w2n.word_to_num(" ".join(phrase))
