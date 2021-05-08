import logging
from typing import Union, List, Tuple

from ._decimal_separator_fixer import DecimalSeparatorFixer
from ._names_fixer import NamesFixer
from ._numbers_fixer import NumberFixer
from ._statistics import StatisticsMarks
from .fixer_configurator import FixerConfigurator, FixerTools


class Fixer:
    """Class fixing text with specific fixers based on given parameters.

    For constructing the fixer some arguments are needed.

    List of supported arguments:
      - `source_lang` - text acronym of language of source sentence
      - `target_lang` - text acronym of language of target sentence
      - `approximately` - flag whenever it  should consider approximation phrases
      - `recalculate` - flag whenever it should change correct units into different ones

    :param arguments: object with arguments values
    """

    def __init__(self, configuration: FixerConfigurator):
        self.fixers = []

        if FixerTools.NAMES in configuration.tools:
            self.fixers.append(NamesFixer(configuration))

        if FixerTools.SEPARATORS in configuration.tools:
            self.fixers.append(DecimalSeparatorFixer(configuration))

        if FixerTools.UNITS in configuration.tools:
            self.fixers.append(NumberFixer(configuration))

        logging.basicConfig(filename='fixer.log', level=logging.ERROR)

    def fix(self, original_text: str, translated_text: str) -> Tuple[Union[str, bool], List]:
        """Function to fix translation of one sentence based on Fixer attributes.

        It caches all exceptions with fixer and when some exception is cached,
        sentence is marked as unfixable.

        :param original_text: Text in source language for verifying the translation.
        :param translated_text: Text translated by translator.
        :return: tuple with fixer output:

            - result of the fixer
                - corrected sentence if it was possible
                - `false` if there is a problem which cannot be fixed
                - `true` is there was found no problem
            - list with flags labeling the sentence and the correction
        """

        final_translated_text = translated_text
        status = True
        final_marks = []

        for tool in self.fixers:
            try:
                output, marks = tool.fix(original_text, final_translated_text)
                final_marks += marks
                if isinstance(output, str):
                    final_translated_text = output
                elif not output:
                    status = False
            except Exception as error:
                logging.error("Error when fixing sentence:\n%s\t%s\nException: %s", original_text, translated_text, error)
                return False, [StatisticsMarks.EXCEPTION_CATCH]

        if final_translated_text != translated_text:
            return final_translated_text, final_marks
        else:
            return True if status else False, final_marks
