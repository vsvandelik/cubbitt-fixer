from typing import List

from ._languages import Language
from .fixer_configurator import FixerConfigurator


class SentencesSplitter:
    """Simple class to split text into paragraphs and sentences."""

    @staticmethod
    def split_text_to_sentences(text: str, language: Language, configuration: FixerConfigurator) -> List[List[str]]:
        """Returns list of paragraphs (list of sentences)"""
        return configuration.lemmatizator.get_sentences_split(text, language)
