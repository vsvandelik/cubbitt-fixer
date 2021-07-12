import json
from abc import ABC, abstractmethod
from typing import List

import requests

from ._languages import Languages, Language


class NameRecognitionException(Exception):
    """Exception raised when there was a problem with the tools for recognising names in sentence."""
    pass


class NameRecognitionInterface(ABC):
    """Interface for tools recognising names in the sentences."""

    @staticmethod
    @abstractmethod
    def get_names(sentence: str, language: Language) -> List[List[str]]:
        pass


class CapitalLettersBasedNameRecognition(NameRecognitionInterface):
    """Naive implementation of NameRecognitionInterface based on capital letters."""

    @staticmethod
    def get_names(sentence: str, language: Language) -> List[List[str]]:
        """Get names in the sentence.

        As a name is considered each word (except the first one) starting with capital letter.

        :param sentence: Source sentence to search in
        :param language: Language of the source sentence
        :return: List of the names (all words with capital letter)
        """
        current_name = []
        cleaned_names = []
        for word in sentence.split()[1:]:
            if word[0].isupper() and word[1:].islower():
                current_name.append(word)
            elif current_name:
                cleaned_names.append(current_name)
                current_name = []

        return cleaned_names


class NameTagApi(NameRecognitionInterface):
    """Wrapper for communicating with NameTag online API.

    NameTag service was developed at UFAL MFF UK and it helps to
    find names in the sentences. It has support for multiple language.

    For each language there is different classification of proper names.

    More info can be found at: https://ufal.mff.cuni.cz/nametag/1/users-manual
    """

    #: URL address of the NameTag online API at LINDAT
    __NAMETAG_URL = "http://lindat.mff.cuni.cz/services/nametag/api/recognize"

    @staticmethod
    def get_names(sentence: str, language: Language) -> List[List[str]]:
        """Get all proper names of person from the sentence.

        It gets NameTag response and filter only names of person.

        When are names next to each other, they are concatenate into one list.

        :param sentence: Source sentence to search names in
        :param language: Language of the source sentence
        :return: List of list with names next to each other
        :raise NameRecognitionException: Exception is thrown when external tool response cannot be downloaded
        """
        model = "&model=english" if language is not Languages.CS else ""
        complete_url = "{}?data={}&output=conll{}".format(NameTagApi.__NAMETAG_URL, sentence, model)
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise NameRecognitionException('It was not possible to connect to the NameTag web service.')

        only_names = []

        parsed_response = json.loads(response.content)

        current_word = []
        for line in parsed_response["result"].split('\n'):
            if line == "":
                continue
            word, type = line.split('\t')
            type_split = type.upper().split('-')
            if type == "O" or not type_split[1].startswith('P'):  # not names
                continue
            if word == "-":
                only_names.append(current_word)
                current_word = []
            elif type[0][0] == "B":  # first part of the name
                only_names.append(current_word)
                current_word = [word]
            else:
                current_word.append(word)

        only_names.append(current_word)

        return only_names[1:]


def get_names_tagger_list():
    return {
        'nametag': NameTagApi,
        'capitalizeLetters': CapitalLettersBasedNameRecognition
    }
