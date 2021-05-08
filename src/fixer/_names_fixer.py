from typing import Union, Tuple, List

from ._languages import Languages
from .fixer_configurator import FixerConfigurator


class NamesFixer:

    def __init__(self, configuration: FixerConfigurator):
        self.configuration = configuration

        self.source_lang = configuration.source_lang
        self.target_lang = configuration.target_lang

    def fix(self, original_sentence: str, translated_sentence: str) -> Tuple[Union[str, bool], List]:
        names_original_sentence = self.configuration.names_tagger.get_names(original_sentence, self.source_lang)

        problems = []

        for name in names_original_sentence:
            if name not in translated_sentence:
                problems.append(name)

        if len(problems) == 0:
            return True, []

        if self.source_lang == Languages.EN:
            alignment = self.configuration.aligner.get_alignment(original_sentence, translated_sentence)
            src_index = 0
        else:
            alignment = self.configuration.aligner.get_alignment(translated_sentence, original_sentence)
            src_index = 1

        translated_sentence_backup = translated_sentence

        for problem in problems:
            for one_problem in problem.split():
                for token in alignment:
                    if token[src_index] == one_problem:
                        translated_sentence = translated_sentence.replace(token[1 - src_index], one_problem)
                        break

        if translated_sentence != translated_sentence_backup:
            return translated_sentence, []

        return False, []
