from .fixer_configurator import FixerConfigurator


class SentencePair:

    def __init__(self, source_text: str, target_text: str, configuration: FixerConfigurator):
        self._source_text = source_text
        self._target_text = self._original_target_text = target_text
        self._configuration = configuration

        self._alignment = None
        self._source_names = None
        self._target_names = None
        self._source_lemmas = None
        self._target_lemmas = None

    @property
    def source_text(self):
        return self._source_text

    @property
    def target_text_has_changed(self):
        return True if self.target_text != self._original_target_text else False

    @property
    def target_text(self):
        return self._target_text

    @target_text.setter
    def target_text(self, value):
        self._target_text = value

    @property
    def alignment(self):
        if not self._alignment:
            self._alignment = self._configuration.aligner.get_alignment(
                self._source_text, self._target_text, self._configuration.source_lang, self._configuration.target_lang)

        return self._alignment

    @property
    def source_names(self):
        if not self._source_names:
            self._source_names = self._configuration.names_tagger.get_names(self._source_text, self._configuration.source_lang)

        return self._source_names

    @property
    def target_names(self):
        if not self._target_names:
            self._target_names = self._configuration.names_tagger.get_names(self._target_text, self._configuration.target_lang)

        return self._target_names

    @property
    def source_lemmas(self):
        if not self._source_lemmas:
            self._source_lemmas = self._configuration.lemmatizator.get_lemmatization(self._source_text, self._configuration.source_lang, False)

        return self._source_lemmas

    @property
    def target_lemmas(self):
        if not self._target_lemmas:
            self._target_lemmas = self._configuration.lemmatizator.get_lemmatization(self._target_text, self._configuration.target_lang, False)

        return self._target_lemmas
