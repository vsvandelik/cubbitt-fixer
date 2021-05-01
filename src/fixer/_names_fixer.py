from typing import Union, Tuple, List

from ._aligner import FastAlignAligner
from ._languages import Language, Languages
from ._name_recognition import NameTagApi


class NamesFixer:

    def __init__(self, source_lang: Language, target_lang: Language):
        self.source_lang = source_lang
        self.target_lang = target_lang

    def fix(self, original_sentence: str, translated_sentence: str) -> Tuple[Union[str, bool], List]:
        names_original_sentence = NameTagApi.get_names(original_sentence, self.source_lang)

        problems = []

        for name in names_original_sentence:
            if name not in translated_sentence:
                problems.append(name)

        if len(problems) == 0:
            return True, []

        if self.source_lang == Languages.EN:
            alignment = FastAlignAligner.get_alignment(original_sentence, translated_sentence)
            src_index = 0
        else:
            alignment = FastAlignAligner.get_alignment(translated_sentence, original_sentence)
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
