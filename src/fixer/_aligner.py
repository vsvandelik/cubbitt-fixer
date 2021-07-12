import json
import re
from abc import ABC, abstractmethod
from typing import Tuple, List

import requests

from ._languages import Language, Languages
from ._units import units


class AlignerException(Exception):
    """Exception raised when there was a problem with the aligner."""
    pass


class AlignerInterface(ABC):
    """Interface for word-aligners in the package.

    Implementations of this interface should provide a word-alignment
    for given sentences.
    """

    @staticmethod
    @abstractmethod
    def get_alignment(src_text: str, trg_text: str, src_lang: Language, trg_lang: Language) -> List[Tuple[str, str]]:
        """Returns word alignment of the sentences based on given languages. Result as list of aligned words."""
        pass


class FastAlignAligner(AlignerInterface):
    """Wrapper for communicating with external online aligner.

    It uses predefined alignment server running at UFAL, MFF. The server uses
    fast_align tool for word-alignment with CzEng2 as dataset.
    """

    _ALIGNER_URL = 'https://quest.ms.mff.cuni.cz/ptakopet-mt380/align/en-cs'

    @staticmethod
    def get_alignment(src_text: str, trg_text: str, src_lang: Language, trg_lang: Language) -> List[Tuple[str, str]]:
        """Returns word alignment given by fast_align.

        Based on given sentences it communicate with external word-aligner tool, which
        returns the pairs of matching indexes and tokenized input sentences.

        :param src_text: Source sentence (cs or en)
        :param trg_text: Translated sentence (cs or en)
        :param src_lang: Language of the source sentence
        :param trg_lang: Language of the translated sentence
        :raises AlignerException: Exception raises when it was not possible to connect to the server
        :return: List of tuples of matching words, first word is in english, second in czech
        """
        if src_lang == Languages.CS:  # source text should be in czech
            temp = src_text
            src_text = trg_text
            trg_text = temp

        payload = json.dumps({
            'src_text': src_text,
            'trg_text': trg_text})
        headers = {'Content-type': 'application/json'}
        response = requests.post(FastAlignAligner._ALIGNER_URL, headers=headers, data=payload)

        if response.status_code != 200:
            raise AlignerException('Aligner was not able to connect to the alignment server.')
        else:
            parsed_response = json.loads(response.content)
            words = []
            for pair in parsed_response['alignment'].split():
                split_pair = pair.split('-')
                left_idx = int(split_pair[0])
                right_idx = int(split_pair[1])
                words.append((parsed_response['src_tokens'][left_idx], parsed_response['trg_tokens'][right_idx]))

            return words


class OrderAligner(AlignerInterface):
    """Simple offline word-aligner based on order of words in sentence.

    This aligner should not be used because of its naivety.

    This aligner returns pairs of word tokens contains units and numbers
    based on given order in sentence. Also it returns proper names identified
    by the first capital letter. It does not recognise whenever the name
    is name of the person of something another.

    Units are mapped to units, numbers as mapped to numbers.
    """

    @staticmethod
    def get_alignment(src_text: str, trg_text: str, src_lang: Language, trg_lang: Language) -> List[Tuple[str, str]]:
        """Returns aligned number, units a names (capitalized tokens)

        Based on order at sentence it returns matching tokens (by categories above).

        :param src_text: Source sentence (cs or en)
        :param trg_text: Translated sentence (cs or en)
        :param src_lang: Language of the source sentence
        :param trg_lang: Language of the translated sentence
        :raises AlignerException: Exception raises when it was not possible to connect to the server
        :return: List of tuples of matching words, first word is in english, second in czech
        """
        tokens_src, _, _, _ = OrderAligner.__get_list_numbers_units_names(src_text, src_lang)
        _, numbers_tokens, units_tokens, names_tokens = OrderAligner.__get_list_numbers_units_names(trg_text, trg_lang)

        output_tokens = []

        for src_token in tokens_src:
            if src_token[0].isdigit() and len(numbers_tokens):  # number
                output_tokens.append((src_token, numbers_tokens[0]))
                numbers_tokens.pop(0)
            elif src_token[0].isdigit():  # number
                output_tokens.append((src_token, None))
            elif src_token[0].isupper() and src_token[1:].islower() and len(names_tokens):  # name
                output_tokens.append((src_token, names_tokens[0]))
                names_tokens.pop(0)
            elif src_token[0].isupper() and src_token[1:].islower():  # name
                output_tokens.append((src_token, None))
            elif len(units_tokens):  # unit
                output_tokens.append((src_token, units_tokens[0]))
                units_tokens.pop(0)
            else:  # unit
                output_tokens.append((src_token, None))

        for number_token in numbers_tokens:
            output_tokens.append((None, number_token))
        for unit_token in units_tokens:
            output_tokens.append((None, unit_token))

        return output_tokens

    @staticmethod
    def __get_list_numbers_units_names(sentence: str, language: Language) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Returns some tokens from the sentence divided into categories

        It process the sentence and extract all interesting parts of it -
        numbers, units and names.

        Each of these categories are returned as separate list.

        :param sentence: Sentence to be process
        :param language: Language of the sentence
        :return: four lists
          - list of all tokens returned in rest ot the lists based on order in the sentence
          - list of all numbers (based on starting with digit)
          - list of all units (based on existence in unit list)
          - list of all names (based on first capital letter)
        """
        tokens = OrderAligner.__tokenize_sentence(sentence)

        selected_tokens = []
        numbers_tokens = []
        units_tokens = []
        names_tokens = []

        units_words = units.get_units_words_list(language)

        for token in tokens:
            if token.lower() in units_words:  # unit
                selected_tokens.append(token)
                units_tokens.append(token)
            elif token[0].isdigit():  # number
                selected_tokens.append(token)
                numbers_tokens.append(token)
            elif token[0].isupper() and token[1:].islower() and token != tokens[0]:  # name
                selected_tokens.append(token)
                names_tokens.append(token)

        return selected_tokens, numbers_tokens, units_tokens, names_tokens

    @staticmethod
    def __tokenize_sentence(sentence: str):
        """Returns sentence divided into separate words (tokens)"""
        clean_sentence = re.sub(r'[\.,!\?](\s|$)', ' ', sentence).strip()
        return clean_sentence.split()


def get_aligners_list():
    return {
        'fast_align': FastAlignAligner,
        'order_based': OrderAligner,
    }
