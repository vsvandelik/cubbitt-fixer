from typing import List

from ._languages import Language
from .fixer_configurator import FixerConfigurator


class SentencesSplitter:

    @staticmethod
    def split_text_to_sentences(text: str, language: Language, configuration: FixerConfigurator) -> List[List[str]]:
        return configuration.lemmatizator.get_sentences_split(text, language)
