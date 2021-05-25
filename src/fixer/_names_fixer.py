from statistics import mode
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
        src_names_only = sentence_pair.source_names
        trg_names_only = sentence_pair.target_names

        if len(src_names_only) == 0 or len(trg_names_only) == 0:
            return True, []

        # Replace if there is only one name
        if len(src_names_only) == 1 and len(trg_names_only) == 1:
            return self.__single_name_in_sentence(sentence_pair, sentence_pair.target_text, src_names_only[0], trg_names_only[0]), [StatisticsMarks.SINGLE_NAME_SENTENCE]

        result_sentence, marks = self.__match_names(sentence_pair)

        if result_sentence is False:
            return False, marks
        elif result_sentence != sentence_pair.target_text:
            return result_sentence, marks
        else:
            return True, [StatisticsMarks.NAMES_CORRECT]

        """
        names_original_sentence = sentence_pair.source_names

        problems = []

        for name in names_original_sentence:
            if name not in sentence_pair.target_text and lemmas[name] not in sentence_pair.target_text:
                problems.append(name)

        if len(problems) == 0:
            return True, [StatisticsMarks.NAMES_CORRECT]

        alignment = sentence_pair.alignment
        src_index = 0 if self.source_lang == Languages.EN else 1

        translated_sentence = sentence_pair.target_text

        names_changed = 0

        for problem in problems:
            changed = False
            for one_problem in problem.split():
                for token in alignment:
                    if token[src_index] == one_problem:
                        translated_sentence = translated_sentence.replace(token[1 - src_index], lemmas[one_problem])
                        changed = True
                        break

            if changed:
                names_changed += 1
        
        if translated_sentence != sentence_pair.target_text:
            return translated_sentence, [StatisticsMarks.NAMES_PROBLEM_FIXED]
        elif names_changed == len(problems):
            return True, [StatisticsMarks.NAMES_CORRECT]

        return False, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]
        """

    def __single_name_in_sentence(self, sentence_pair: SentencePair, target_text: str, source_name: List[str], target_name: List[str]) -> Union[str, bool]:
        if source_name == target_name:
            return target_text

        lemmas = {word["word"]: word["lemma"] for word in sentence_pair.source_lemmas}
        lemmas_source_names = [lemmas[name] for name in source_name]

        return target_text.replace(" ".join(target_name), " ".join(lemmas_source_names))

    def __match_names(self, sentence_pair: SentencePair):
        alignment = sentence_pair.alignment

        src_alignment = 0 if self.source_lang == Languages.EN else 1
        uses_of_target_names = len(sentence_pair.target_names) * [0]
        matches = []

        for source_name in sentence_pair.source_names:
            possible_alignments = set()
            for token in source_name:
                possible_alignments.update([align[1 - src_alignment] for align in alignment if align[src_alignment] == token])

            possible_target_names_idxs = []

            for possible_alignment in possible_alignments:
                for idx, target_name in enumerate(sentence_pair.target_names):
                    if possible_alignment in target_name:
                        possible_target_names_idxs.append(idx)

            if not possible_target_names_idxs:
                return False, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]
            selected_target_name = mode(possible_target_names_idxs)
            matches.append((source_name, sentence_pair.target_names[selected_target_name]))
            uses_of_target_names[selected_target_name] += 1

        matches_to_remove = []
        for idx, use_of_target_names in enumerate(uses_of_target_names):
            if use_of_target_names > 1:
                for match_id, match in enumerate(matches):
                    if match[1] == sentence_pair.target_names[idx]:
                        matches_to_remove.append(match_id)

        if len(matches_to_remove) == len(matches):
            return False, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]

        translated_sentence = sentence_pair.target_text
        for match_id, match in enumerate(matches):
            if match_id in matches_to_remove:
                continue
            translated_sentence = self.__single_name_in_sentence(sentence_pair, translated_sentence, match[0], match[1])

        return translated_sentence, [StatisticsMarks.MULTIPLE_NAMES_SENTENCE]
