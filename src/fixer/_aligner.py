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
    for given sentence in en-cs.

    Minimum requirement is returning word-alignment for numbers and units.
    """

    @staticmethod
    @abstractmethod
    def get_alignment(src_text: str, trg_text: str) -> List[Tuple[str, str]]:
        """Main alignment method returning the word-alignment."""
        pass


class FastAlignAligner(AlignerInterface):
    """Support class for communicating with the external aligner server.

    It uses predefined alignment server running at UFAL, MFF. The server uses
    fast_align tool for word-alignment with CzEng2 as dataset.
    """

    _ALIGNER_URL = 'https://quest.ms.mff.cuni.cz/ptakopet-mt380/align/en-cs'

    @staticmethod
    def get_alignment(src_text: str, trg_text: str) -> List[Tuple[str, str]]:
        """Static method for getting a word-alignment of pair of english and czech sentences.

        Based on given sentences it communicate with external word-aligner tool, which
        returns the pairs of matching indexes and tokenized input sentences.

        :param src_text: Sentence in english
        :param trg_text: Sentence in czech
        :raises AlignerException: Exception raises when it was not possible to connect to the server
        :return: List of tuples of matching words, first word is in english, second in czech
        """
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
    """Backup offline word-aligner based on order of words in sentence.

    This aligner should be used when it is not possible to connect to the
    external aligner.

    This aligner returns pairs of word tokens contains units and numbers
    based on given order in sentence.

    Units are mapped to units, numbers as mapped to numbers.
    """

    @staticmethod
    def _tokenize_sentence(sentence: str):
        clean_sentence = re.sub(r'[\.,!\?](\s|$)', ' ', sentence).strip()
        return clean_sentence.split()

    @staticmethod
    def _get_list_numbers_units(sentence: str, language: Language) -> Tuple[List[str], List[str], List[str]]:
        """Returns three list (list of all units and numbers based on order, list of numbers, list of units)"""
        tokens = OrderAligner._tokenize_sentence(sentence)

        selected_tokens = []
        numbers_tokens = []
        units_tokens = []
        units_words = units.get_units_words_list(language)

        for token in tokens:
            if token.lower() in units_words:  # unit
                selected_tokens.append(token)
                units_tokens.append(token)
            elif token[0].isdigit():  # number
                selected_tokens.append(token)
                numbers_tokens.append(token)

        return selected_tokens, numbers_tokens, units_tokens

    @staticmethod
    def get_alignment(src_text: str, trg_text: str) -> List[Tuple[str, str]]:
        """Returns only units and numbers word alignment based on order in sentence.

        It extracts list of numbers and units from both sentences and mapped
        those lists between languages.

        :param src_text: Sentence in english
        :param trg_text: Sentence in czech
        :return: List of tuples of matching words (only units and numbers), first word is in english, second in czech
        """
        tokens_src, _, _ = OrderAligner._get_list_numbers_units(src_text, Languages.EN)
        _, numbers_tokens, units_tokens = OrderAligner._get_list_numbers_units(trg_text, Languages.CS)

        output_tokens = []

        for src_token in tokens_src:
            if src_token[0].isdigit() and len(numbers_tokens):  # number
                output_tokens.append((src_token, numbers_tokens[0]))
                numbers_tokens.pop(0)
            elif src_token[0].isdigit():  # number
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


def get_aligners_list():
    return {
        'fast_align': FastAlignAligner,
        'order_based': OrderAligner,
    }
