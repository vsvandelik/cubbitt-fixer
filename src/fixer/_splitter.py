from typing import Tuple, List

from ._custom_types import Number
from ._languages import Language
from ._units import Unit, units


class StringToNumberUnitConverter:

    @staticmethod
    def __convert_text_to_inches(text: str) -> int:
        """Convert number written as feet and inches (6'12") to inches"""
        feet = 0
        feet_idx_end = None
        inches = 0
        for idx, l in enumerate(text):
            if l == "'":
                feet = int(text[:idx])
                feet_idx_end = idx
            elif l == '"':
                inches = int(text[feet_idx_end + 1:idx])

        return inches + 12 * feet
