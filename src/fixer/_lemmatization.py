import json
import os
from abc import ABC, abstractmethod
from typing import List

import requests
from conllu import parse
from ufal.udpipe import Model, Pipeline, ProcessingError

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
    def get_lemmatization(src_text: str, language: Language, only_numbers=True) -> List[dict]:
        """Main alignment method returning the word-alignment."""
        pass

    @staticmethod
    @abstractmethod
    def get_sentences_split(src_text: str, language: Language) -> List[List[str]]:
        pass


class UDPipeProcessor:

    @staticmethod
    def process_udpipe_output(conllu_string: str, only_numbers: bool):
        lemmas = []

        for sentence in parse(conllu_string):
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

    @staticmethod
    def split_by_paragraphs_sentences(conllu_string: str) -> List[List[str]]:
        paragraphs = []
        actual_paragraph = []

        for sentence in parse(conllu_string):
            metadata = sentence.metadata
            if 'newpar' in metadata and actual_paragraph:
                paragraphs.append(actual_paragraph)
                actual_paragraph = []

            actual_paragraph.append(metadata['text'])

        paragraphs.append(actual_paragraph)

        return paragraphs


class UDPipeApi(LemmatizationInterface):
    """Class for communicating with external web service UDPipe.

    UDPipe was developed at UFAL MFF CUNI. Based on GET request it returns
    lemmatization among others. The response is in CoNLL-U format.
    """
    _UDPIPE_URL = "http://lindat.mff.cuni.cz/services/udpipe/api/process"

    @staticmethod
    def _do_http_request(src_text: str, language: Language, operations: str) -> dict:
        model = "&model=en" if language is not Languages.CS else ""
        complete_url = "{}?{}{}&data={}".format(UDPipeApi._UDPIPE_URL, operations, model, src_text)
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise LemmatizationException('UDPIPE was not able to connect to the UDPipe web service.')

        return json.loads(response.content)

    @staticmethod
    def get_lemmatization(src_text: str, language: Language, only_numbers=True) -> List[dict]:
        """Get pairs of words and its lemmas in given language."""

        response = UDPipeApi._do_http_request(src_text, language, "tokenizer=ranges&tagger&parser")
        return UDPipeProcessor.process_udpipe_output(response['result'], only_numbers)

    @staticmethod
    def get_sentences_split(src_text: str, language: Language) -> List[List[str]]:
        response = UDPipeApi._do_http_request(src_text, language, "tokenizer=ranges")
        return UDPipeProcessor.split_by_paragraphs_sentences(response['result'])


class UDPipeOffline(LemmatizationInterface):
    _MODEL_PATH = 'models/'
    _CZECH_MODEL_NAME = 'czech-pdt-ud-2.5-191206.udpipe'
    _ENGLISH_MODEL_NAME = 'english-ewt-ud-2.5-191206.udpipe'
    _LINDAT_BASE_URL = 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/'

    def __init__(self):
        self._verify_download_file(UDPipeOffline._CZECH_MODEL_NAME)
        self._verify_download_file(UDPipeOffline._ENGLISH_MODEL_NAME)

        self._czech_model = Model.load(UDPipeOffline._MODEL_PATH + UDPipeOffline._CZECH_MODEL_NAME)
        self._english_model = Model.load(UDPipeOffline._MODEL_PATH + UDPipeOffline._ENGLISH_MODEL_NAME)

        self._czech_pipeline = Pipeline(self._czech_model, 'tokenizer=ranges', Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
        self._english_pipeline = Pipeline(self._english_model, 'tokenizer=ranges', Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")

    @staticmethod
    def _verify_download_file(model_name):
        if not os.path.isdir(UDPipeOffline._MODEL_PATH):
            try:
                os.mkdir(UDPipeOffline._MODEL_PATH)
            except OSError:
                raise LemmatizationException("Creation of the directory %s failed" % UDPipeOffline._MODEL_PATH)

        if not os.path.isfile(UDPipeOffline._MODEL_PATH + model_name):
            r = requests.get(UDPipeOffline._LINDAT_BASE_URL + model_name)
            if r.status_code != 200:
                raise LemmatizationException("Cannot download the offline model for the UDPipe")

            open(UDPipeOffline._MODEL_PATH + model_name, 'wb').write(r.content)

        if not os.path.isfile(UDPipeOffline._MODEL_PATH + model_name):
            raise LemmatizationException("Cannot prepare the model")

    def get_lemmatization(self, src_text: str, language: Language, only_numbers=True) -> List[dict]:
        pipeline = self._english_pipeline if language is not Languages.CS else self._czech_pipeline

        error = ProcessingError()

        processed = pipeline.process(src_text, error)
        if error.occurred():
            raise LemmatizationException("Cannot get the lemmatization from the UDPipe service:" + error.message)

        return UDPipeProcessor.process_udpipe_output(processed, only_numbers)

    def get_sentences_split(self, src_text: str, language: Language) -> List[List[str]]:
        model = self._english_model if language is not Languages.CS else self._czech_model
        pipeline = Pipeline(model, 'tokenizer=ranges', Pipeline.NONE, Pipeline.NONE, "conllu")
        error = ProcessingError()

        processed = pipeline.process(src_text, error)
        if error.occurred():
            raise LemmatizationException("Cannot get the lemmatization from the UDPipe service:" + error.message)

        return UDPipeProcessor.split_by_paragraphs_sentences(processed)


def get_lemmatizators_list():
    return {
        'udpipe_online': UDPipeApi,
        'udpipe_offline': UDPipeOffline
    }
