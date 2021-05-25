import json
from abc import ABC, abstractmethod
from typing import List, Tuple

import requests

from ._languages import Languages, Language


class NameRecognitionException(Exception):
    pass


class NameRecognitionInterface(ABC):

    @staticmethod
    @abstractmethod
    def get_names(sentence: str, language: Language) -> List[List[str]]:
        pass


class CapitalLettersBasedNameRecognition(NameRecognitionInterface):

    @staticmethod
    def get_names(sentence: str, language: Language) -> List[str]:
        cleaned_names = []
        for word in sentence.split()[1:]:
            if word[0].isupper():
                cleaned_names.append(word)

        return cleaned_names


class NameTagApi(NameRecognitionInterface):
    _NAMETAG_URL = "http://lindat.mff.cuni.cz/services/nametag/api/recognize"

    @staticmethod
    def get_names(sentence: str, language: Language) -> List[List[str]]:
        model = "&model=english" if language is not Languages.CS else ""
        complete_url = "{}?data={}&output=conll{}".format(NameTagApi._NAMETAG_URL, sentence, model)
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
            type_split = type.split('-')
            if type == "O" or not type_split[1].startswith('P'):
                continue
            if word == "-":
                only_names.append(current_word)
                current_word = []
            elif type[0][0] == "B":
                only_names.append(current_word)
                current_word = [word]
            else:
                current_word.append(word)

        only_names.append(current_word)

        return only_names[1:]

        """for line in parsed_response['result'].split('\n'):
            if not line:
                continue
            entity_range, entity_type, entity_text = line.split('\t')
            if not entity_type.lower().startswith('p'):  # removed non persons
                continue
            names[entity_range] = entity_text

        cleaned_names = []
        for key, name in names.items():
            if ',' not in key:
                cleaned_names.append(name)

            tokens = key.split(',')
            satisfied = 0
            for token in tokens:
                if token in names.keys():
                    satisfied += 1

            if satisfied != len(tokens):
                cleaned_names.append(name)

        return cleaned_names
        """


def get_names_tagger_list():
    return {
        'nametag': NameTagApi
    }
