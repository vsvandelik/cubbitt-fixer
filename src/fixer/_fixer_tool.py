from abc import ABC, abstractmethod
from typing import List, Tuple

from ._sentence_pair import SentencePair
from .fixer_statistics import FixerStatisticsMarks as StatisticsMarks


class FixerToolInterface(ABC):
    """Main interface which should all fixing tool implement."""

    @abstractmethod
    def fix(self, sentence_pair: SentencePair) -> Tuple[str, List[StatisticsMarks]]:
        pass
