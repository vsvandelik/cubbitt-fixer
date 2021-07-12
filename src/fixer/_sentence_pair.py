from typing import List, Tuple

from .fixer_configurator import FixerConfigurator


class SentencePair:
    """Main data class holding information about source and translated sentence.

    Mainly the output of externals tools are saved into this class so they do not
    need to be called again.
    """

    def __init__(self, source_text: str, target_text: str, configuration: FixerConfigurator):
        """
        :param source_text: Original text from the user
        :param target_text: Translated text from the translator
        :param configuration: Configuration of the tool
        """
        self.__source_text = source_text
        self.__target_text = self.__original_target_text = target_text
        self.__configuration = configuration

        self.__alignment = None
        self.__source_names = None
        self.__target_names = None
        self.__source_lemmas = None
        self.__target_lemmas = None

    @property
    def source_text(self) -> str:
        """Original text from the user"""
        return self.__source_text

    @property
    def target_text_has_changed(self) -> bool:
        """Indicator whenever the translated text changed"""
        return True if self.__target_text != self.__original_target_text else False

    @property
    def target_text(self) -> str:
        """Translated text from the translator"""
        return self.__target_text

    @target_text.setter
    def target_text(self, value: str):
        """Change the target text"""
        self.__target_text = value

    @property
    def alignment(self) -> List[Tuple[str, str]]:
        """Word alignment of original to translated sentence"""
        if not self.__alignment:
            self.__alignment = self.__configuration.aligner.get_alignment(
                self.__source_text, self.__target_text, self.__configuration.source_lang, self.__configuration.target_lang)

        return self.__alignment

    @property
    def source_names(self) -> List[List[str]]:
        """List of names in original sentence"""
        if not self.__source_names:
            self.__source_names = self.__configuration.names_tagger.get_names(self.__source_text, self.__configuration.source_lang)

        return self.__source_names

    @property
    def target_names(self) -> List[List[str]]:
        """List of names in translated sentence"""
        if not self.__target_names:
            self.__target_names = self.__configuration.names_tagger.get_names(self.__target_text, self.__configuration.target_lang)

        return self.__target_names

    @property
    def source_lemmas(self) -> List[dict]:
        """Original sentence analysis"""
        if not self.__source_lemmas:
            self.__source_lemmas = self.__configuration.lemmatizator.get_lemmatization(self.__source_text, self.__configuration.source_lang)

        return self.__source_lemmas

    @property
    def target_lemmas(self) -> List[dict]:
        """Translated sentence analysis"""
        if not self.__target_lemmas:
            self.__target_lemmas = self.__configuration.lemmatizator.get_lemmatization(self.__target_text, self.__configuration.target_lang)

        return self.__target_lemmas
