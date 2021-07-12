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
    def get_lemmatization(src_text: str, language: Language) -> List[dict]:
        """Main alignment method returning the word-alignment."""
        pass

    @staticmethod
    @abstractmethod
    def get_sentences_split(src_text: str, language: Language) -> List[List[str]]:
        pass


class UDPipeProcessor:

    @staticmethod
    def process_udpipe_output(conllu_string: str) -> List[dict]:
        """Parse output of the UDPipe in Conllu format."""
        lemmas = []

        for sentence in parse(conllu_string):
            for token in sentence:
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
        """Split given text into paragraphs and sentences based on conllu UDPipe response."""
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


class UDPipeOnline(LemmatizationInterface):
    """Class for communicating with external web service UDPipe.

    UDPipe was developed at UFAL MFF CUNI. Based on GET request it returns
    lemmatization among others. The response is in CoNLL-U format.
    """

    #: URL address of API of UDPipe tool
    __UDPIPE_URL = "http://lindat.mff.cuni.cz/services/udpipe/api/process"

    @staticmethod
    def __do_http_request(src_text: str, language: Language, operations: str) -> dict:
        """Provide a HTTP GET request to online UDPipe API, parse JSON response

        :param src_text: Source text to be send to UDPipe
        :param language: Language of the source text
        :param operations: List of tools to be run by UDPipe (tokenizer, tagger, parser, etc.)
        :return: Parsed JSON object
        """
        model = "&model=en" if language is not Languages.CS else ""
        complete_url = "{}?{}{}&data={}".format(UDPipeOnline.__UDPIPE_URL, operations, model, src_text)
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise LemmatizationException('UDPIPE was not able to connect to the UDPipe web service.')

        return json.loads(response.content)

    @staticmethod
    def get_lemmatization(src_text: str, language: Language) -> List[dict]:
        """Get sentence analysis of the given sentence from online UDPipe"""

        response = UDPipeOnline.__do_http_request(src_text, language, "tokenizer=ranges&tagger&parser")
        return UDPipeProcessor.process_udpipe_output(response['result'])

    @staticmethod
    def get_sentences_split(src_text: str, language: Language) -> List[List[str]]:
        """Use online UDPipe to divide source text into paragraphs and sentences"""

        response = UDPipeOnline.__do_http_request(src_text, language, "tokenizer=ranges")
        return UDPipeProcessor.split_by_paragraphs_sentences(response['result'])


class UDPipeOffline(LemmatizationInterface):
    """Class for communicating with locally installed UDPipe

    UDPipe was developed at UFAL MFF CUNI. This class uses it as
    a python package which is wrapper on origin C++ tool.

    It downloads models from internet if they are not downloaded yet.
    """

    #: Path to models
    __MODEL_PATH = 'models/'

    #: Name of the czech UDPipe model
    __CZECH_MODEL_NAME = 'czech-pdt-ud-2.5-191206.udpipe'

    #: Name of the english UDPipe model
    __ENGLISH_MODEL_NAME = 'english-ewt-ud-2.5-191206.udpipe'

    #: URL address to download models from
    __LINDAT_BASE_URL = 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/'

    def __init__(self):
        self.__verify_download_file(UDPipeOffline.__CZECH_MODEL_NAME)
        self.__verify_download_file(UDPipeOffline.__ENGLISH_MODEL_NAME)

        self.__czech_model = Model.load(UDPipeOffline.__MODEL_PATH + UDPipeOffline.__CZECH_MODEL_NAME)
        self.__english_model = Model.load(UDPipeOffline.__MODEL_PATH + UDPipeOffline.__ENGLISH_MODEL_NAME)

        self.__czech_pipeline = Pipeline(self.__czech_model, 'tokenizer=ranges', Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
        self.__english_pipeline = Pipeline(self.__english_model, 'tokenizer=ranges', Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")

    @staticmethod
    def __verify_download_file(model_name: str):
        """Verifies whenever the models are locally downloaded. Downloads them if necessary.

        :param model_name: Name of the model to be downloaded
        :raise LemmatizationException: Expcetion thrown when models cannot be downloaded or save.
        """
        if not os.path.isdir(UDPipeOffline.__MODEL_PATH):  # verifies existence (or create) folder for models
            try:
                os.mkdir(UDPipeOffline.__MODEL_PATH)
            except OSError:
                raise LemmatizationException("Creation of the directory %s failed" % UDPipeOffline.__MODEL_PATH)

        if not os.path.isfile(UDPipeOffline.__MODEL_PATH + model_name):  # verifies existence (or download) models
            r = requests.get(UDPipeOffline.__LINDAT_BASE_URL + model_name)
            if r.status_code != 200:
                raise LemmatizationException("Cannot download the offline model for the UDPipe")

            open(UDPipeOffline.__MODEL_PATH + model_name, 'wb').write(r.content)

        if not os.path.isfile(UDPipeOffline.__MODEL_PATH + model_name):  # verifies existence models
            raise LemmatizationException("Cannot prepare the model")

    def get_lemmatization(self, src_text: str, language: Language) -> List[dict]:
        """Get sentence analysis of the given sentence from offline UDPipe

        :param src_text: Source text to be analysed
        :param language: Language of the source test
        :return: List of tokens with analysis
        :raise LemmatizationException: Raised when external library cannot process the sentence
        """
        pipeline = self.__english_pipeline if language is not Languages.CS else self.__czech_pipeline

        error = ProcessingError()

        processed = pipeline.process(src_text, error)
        if error.occurred():
            raise LemmatizationException("Cannot get the lemmatization from the UDPipe service:" + error.message)

        return UDPipeProcessor.process_udpipe_output(processed)

    def get_sentences_split(self, src_text: str, language: Language) -> List[List[str]]:
        """Use offline UDPipe to divide source text into paragraphs and sentences

        :raise LemmatizationException: Raised when external library cannot process the sentence
        """
        model = self.__english_model if language is not Languages.CS else self.__czech_model
        pipeline = Pipeline(model, 'tokenizer=ranges', Pipeline.NONE, Pipeline.NONE, "conllu")
        error = ProcessingError()

        processed = pipeline.process(src_text, error)
        if error.occurred():
            raise LemmatizationException("Cannot get the lemmatization from the UDPipe service:" + error.message)

        return UDPipeProcessor.split_by_paragraphs_sentences(processed)


def get_lemmatizators_list():
    return {
        'udpipe_online': UDPipeOnline,
        'udpipe_offline': UDPipeOffline
    }
