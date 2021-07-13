import logging
from typing import List, Tuple

from ._decimal_separator_fixer import DecimalSeparatorFixer
from ._names_fixer import NamesFixer
from ._numbers_fixer import NumberFixer
from ._sentence_pair import SentencePair
from .fixer_configurator import FixerConfigurator, FixerTools
from .fixer_statistics import FixerStatisticsMarks as StatisticsMarks


class Fixer:
    """Class fixing text with specific fixers based on given parameters.

    Supported operations are:
      - checking and replacement of separators (decimal, thousands)
      - checking and replacement of proper names of person
      - checkong and replacement of numbers (possible with units)

    All exceptions are catched and logged into 'fixer.log' file.

    :param configuration: Configuration instance
    """

    def __init__(self, configuration: FixerConfigurator):
        self.fixers = []
        self.configuration = configuration

        if FixerTools.NAMES in configuration.tools:
            self.fixers.append(NamesFixer(configuration))

        if FixerTools.SEPARATORS in configuration.tools:
            self.fixers.append(DecimalSeparatorFixer(configuration))

        if FixerTools.UNITS in configuration.tools:
            self.fixers.append(NumberFixer(configuration))

        logging.basicConfig(filename='fixer.log', level=logging.ERROR)

    def fix(self, original_text: str, translated_text: str) -> Tuple[str, bool, List[StatisticsMarks]]:
        """Function to fix translation of one sentence based on Fixer attributes.

        It caches all exceptions with fixer and when some exception is cached,
        sentence is marked as unfixable.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return:    - sentence after fixing (possible the same as input)
                    - has changed flag
                    - list with flags labeling the sentence and the correction

        """

        sentence_pair = SentencePair(original_text, translated_text, self.configuration)

        final_marks = []

        for tool in self.fixers:
            try:
                sentence_pair.target_text, marks = tool.fix(sentence_pair)
                final_marks += marks
            except Exception as error:
                logging.error("Error when fixing sentence:\n%s\t%s\nException: %s", original_text, translated_text, error)
                return sentence_pair.target_text, sentence_pair.target_text_has_changed, [StatisticsMarks.G_EXCEPTION_CATCH]

        return sentence_pair.target_text, sentence_pair.target_text_has_changed, final_marks
