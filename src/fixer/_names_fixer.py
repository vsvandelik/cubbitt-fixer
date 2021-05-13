from typing import Union, Tuple, List

from ._languages import Languages
from ._sentence_pair import SentencePair
from ._statistics import StatisticsMarks
from .fixer_configurator import FixerConfigurator


class NamesFixer:

    def __init__(self, configuration: FixerConfigurator):
        self.configuration = configuration

        self.source_lang = configuration.source_lang
        self.target_lang = configuration.target_lang

    def fix(self, sentence_pair: SentencePair) -> Tuple[Union[str, bool], List]:
        names_original_sentence = sentence_pair.source_names

        problems = []

        for name in names_original_sentence:
            if name not in sentence_pair.target_text:
                problems.append(name)

        if len(problems) == 0:
            return True, []

        alignment = sentence_pair.alignment
        src_index = 0 if self.source_lang == Languages.EN else 1

        translated_sentence = sentence_pair.target_text

        for problem in problems:
            for one_problem in problem.split():
                for token in alignment:
                    if token[src_index] == one_problem:
                        translated_sentence = sentence_pair.target_text.replace(token[1 - src_index], one_problem)
                        break

        if translated_sentence != sentence_pair.target_text:
            return translated_sentence, [StatisticsMarks.NAMES_PROBLEM_FIXED]

        return False, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]
