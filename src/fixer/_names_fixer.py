from statistics import mode
from typing import Tuple, List, Optional

from ._languages import Languages
from ._sentence_pair import SentencePair
from ._statistics import StatisticsMarks
from .fixer_configurator import FixerConfigurator


class NamesFixer:
    """Fixer of wrong translation of proper names of person

    Via external tools for recognising proper names of person it
    check whenever tha name is in the same form in translated sentence
    and if not it replace the wrong translation.

    Names in source and translated sentence are aligned with external
    aligner.
    """

    def __init__(self, configuration: FixerConfigurator):
        """
        :param configuration: Configuration of the package
        """
        self.configuration = configuration

        self.source_lang = configuration.source_lang
        self.target_lang = configuration.target_lang

    def fix(self, sentence_pair: SentencePair) -> Tuple[str, List[StatisticsMarks]]:
        """It verifies whenever the sentence contains problem and tries to fix it

        If there is only name name in source and translated sentence,
        those are automaticly matched together.

        For more names the external aligner is called.

        :param sentence_pair: Internal class with details about the sentence and translation
        :return: Possible repaired sentence and statistics
        """
        src_names_only = sentence_pair.source_names
        trg_names_only = sentence_pair.target_names

        if len(src_names_only) == 0 or len(trg_names_only) == 0:
            return sentence_pair.target_text, []

        # Replace if there is only one name
        if len(src_names_only) == 1 and len(trg_names_only) == 1:
            single_name_result, has_changed = self.__single_name_in_sentence(sentence_pair, sentence_pair.target_text, src_names_only[0], trg_names_only[0])
            return single_name_result, has_changed, [StatisticsMarks.SINGLE_NAME_SENTENCE] + [StatisticsMarks.NAMES_CORRECT] if not has_changed else []

        result_sentence, marks = self.__match_names(sentence_pair)

        if result_sentence is None:
            return sentence_pair.target_text, marks
        else:
            return result_sentence, marks if result_sentence != sentence_pair.target_text else [StatisticsMarks.NAMES_CORRECT]

    def __single_name_in_sentence(self, sentence_pair: SentencePair, target_text: str, source_name: List[str], target_name: List[str]) -> Tuple[str, bool]:
        """"Replace name in translated sentence for the name in source sentence.

        Lemmas of the names are used as the replacement.
        :param sentence_pair: Information about source and translated sentnce
        :param target_text: Translated sentence with possible changes
        :param source_name: Name in source sentence
        :param target_name: Name in translated sentence
        :return: target text with replaced name and flag if there was any change
        """
        if source_name == target_name:
            return target_text, False

        lemmas = {word["word"]: word["lemma"] for word in sentence_pair.source_lemmas}
        lemmas_source_names = [lemmas[name] for name in source_name]

        return target_text.replace(" ".join(target_name), " ".join(lemmas_source_names)), True

    def __match_names(self, sentence_pair: SentencePair) -> Tuple[Optional[str], List[StatisticsMarks]]:
        """It align names tokens in source and translated sentence

        If any word from source sentence is aligned (via external aligner) to any word
        in translated sentence, those names are matched.

        If more than one name is matched to some name in translated sentence,
        those source names are ignored.

        After finishing the matching, the the replacement method is called.

        :param sentence_pair: Information about source and translated sentence
        :return: two values
          - string if some name was changed
          - list of statistics marks
        """
        alignment = sentence_pair.alignment

        src_alignment = 0 if self.source_lang == Languages.EN else 1
        uses_of_target_names = len(sentence_pair.target_names) * [0]
        matches = []

        for source_name in sentence_pair.source_names:
            possible_alignments = set()
            for token in source_name:  # find translated tokens aligned with token from source names
                possible_alignments.update([align[1 - src_alignment] for align in alignment if align[src_alignment] == token])

            possible_target_names_idxs = []

            # find possible translated names
            for possible_alignment in possible_alignments:
                for idx, target_name in enumerate(sentence_pair.target_names):
                    if possible_alignment in target_name:
                        possible_target_names_idxs.append(idx)

            if not possible_target_names_idxs:
                return None, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]

            selected_target_name = mode(possible_target_names_idxs)  # select name with the most matched words
            matches.append((source_name, sentence_pair.target_names[selected_target_name]))
            uses_of_target_names[selected_target_name] += 1

        #  remove matches with more than one matched source name to one translated name
        matches_to_remove = []
        for idx, use_of_target_names in enumerate(uses_of_target_names):
            if use_of_target_names > 1:
                for match_id, match in enumerate(matches):
                    if match[1] == sentence_pair.target_names[idx]:
                        matches_to_remove.append(match_id)

        if len(matches_to_remove) == len(matches):
            return None, [StatisticsMarks.NAMES_PROBLEM_UNFIXABLE]

        translated_sentence = sentence_pair.target_text
        for match_id, match in enumerate(matches):
            if match_id in matches_to_remove:
                continue
            translated_sentence = self.__single_name_in_sentence(sentence_pair, translated_sentence, match[0], match[1])

        return translated_sentence, [StatisticsMarks.MULTIPLE_NAMES_SENTENCE]
