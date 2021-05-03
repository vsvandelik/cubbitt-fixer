import json
from abc import ABC, abstractmethod
from typing import Dict, List

import requests
from conllu import parse

from ._languages import Language, Languages


class LemmatizationException(Exception):
    """Exception raised when there was a problem with the lemmatization tool."""
    pass


class LemmatizationInterface(ABC):
    """Interface for working with lemmatization tools.

    Implementations of this interface should provide a lemmatization of
    a given sentence / text.
    """

    @staticmethod
    @abstractmethod
    def get_lemmatization(src_text: str, languge: Language) -> Dict[str, str]:
        """Main alignment method returning the word-alignment."""
        pass


class UDPipeApi(LemmatizationInterface):
    """Class for communicating with external web service UDPipe.

    UDPipe was developed at UFAL MFF CUNI. Based on GET request it returns
    lemmatization among others. The response is in CoNLL-U format.
    """
    _UDPIPE_URL = "http://lindat.mff.cuni.cz/services/udpipe/api/process"

    @staticmethod
    def get_lemmatization(src_text: str, language: Language, only_numbers=True) -> List[dict]:
        """Get pairs of words and its lemmas in given language."""

        model = "&model=en" if language is not Languages.CS else ""
        complete_url = "{}?tokenizer=ranges&tagger&parser{}&data={}".format(UDPipeApi._UDPIPE_URL, model, src_text)
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise LemmatizationException('UDPIPE was not able to connect to the UDPipe web service.')

        lemmas = []

        parsed_response = json.loads(response.content)
        for sentence in parse(parsed_response['result']):
            for token in sentence.filter(upostag="NUM") if only_numbers else sentence:
                if not token['misc']:
                    continue
                token_start, token_end = token['misc']['TokenRange'].split(':')
                lemmas.append({
                    'upostag': token['upos'],
                    'word': token['form'],
                    'lemma': token['lemma'],
                    'rangeStart': int(token_start),
                    'rangeEnd': int(token_end)
                })

        return lemmas


def get_lemmatizators_list():
    return {
        'udpipe': UDPipeApi
    }
