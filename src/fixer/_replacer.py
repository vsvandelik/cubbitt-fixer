from typing import Tuple, Optional

from ._custom_types import *
from ._finder import NumberUnitFinderResult
from ._languages import Language, Languages
from ._units import Unit, units


class Replacer:
    """Supporting class for replacing strings in broken sentences

    The class contains static methods for specific replacement algorithms.
    """

    @staticmethod
    def replace_unit(sentence: str, source_number_unit: NumberUnitFinderResult, target_number_unit: NumberUnitFinderResult, new_unit: Unit, language: Language) -> str:
        """Replace only unit within the broken sentence

        Based on new unit it decides whenever the unit should be put. When the new unit
        has flag "before number", the replacer returns unit before number.

        For units before number with length 1 there is no space between unit and number.
        For units after number there is number is first letter of unit is alphabet char.

        :param sentence: Sentence to be replaced in
        :param source_number_unit: NumberUnit part from the source sentence
        :param target_number_unit: NumberUnit part from the target sentence
        :param new_unit: Unit to be replaced with
        :param language: Language of the sentence to be replaced in
        :return: Sentence with replaced wrong unit
        """

        translated_number = target_number_unit.text_part.replace(target_number_unit.unit.word, "").strip(' ,-')

        # Backup of replacing only with the acronyms
        # if new_unit.before_number and source_number_unit.scaling:
        #    non_abbreviation_unit = units.get_correct_unit(language, target_number_unit.number, target_number_unit.unit, new_unit, new_unit.category, abbreviation=False)
        #    new_number_unit_part = f"{translated_number} {non_abbreviation_unit.word}"

        if new_unit.before_number and len(new_unit.word) == 1:  # eg. $250
            new_number_unit_part = f"{new_unit.word}{translated_number}"

        elif new_unit.before_number:  # eg. CZK 250
            new_number_unit_part = f"{new_unit.word} {translated_number}"

        elif target_number_unit.modifier and new_unit.language == Languages.EN:  # eg. 250-metre
            singular_unit = units.get_correct_unit(Languages.EN, 1, source_number_unit.unit, strict_category=new_unit.category, modifier=True)
            new_number_unit_part = f"{translated_number}-{singular_unit.word}"

        elif not new_unit.word[0].isalpha():  # 250,-kč
            new_number_unit_part = f"{translated_number}{new_unit.word}"

        else:
            new_number_unit_part = f"{translated_number} {new_unit.word}"

        return sentence.replace(target_number_unit.text_part.strip(), new_number_unit_part).replace("  ", " ")

    @staticmethod
    def replace_number(sentence: str, source_number_unit: NumberUnitFinderResult, target_number_unit: NumberUnitFinderResult, language: Language, original_target_number: str) -> str:
        """Replace only number within the broken sentence

        In the given part of the sentence the number is replaced for another number.
        The given number is rounded and the scaling is added.

        :param sentence: Sentence to be replaced in
        :param source_number_unit: NumberUnit part from the source sentence
        :param target_number_unit: NumberUnit part from the target sentence
        :param language: Language of the sentence to be replaced in
        :param original_target_number: Striped number as it was in original translated sentence
        :return: Sentence with replaced wrong number
        """

        new_number = Replacer.__round_to_valid_digits(source_number_unit.number, source_number_unit.number)
        new_number, _ = Replacer.__add_scaling_word(source_number_unit, target_number_unit, new_number, language)

        with_new_number = target_number_unit.text_part.replace(original_target_number, new_number)
        return sentence.replace(target_number_unit.text_part, with_new_number)

    @staticmethod
    def replace_unit_number(sentence: str, source_number_unit: NumberUnitFinderResult, target_number_unit: NumberUnitFinderResult, new_number: Number, new_unit: Unit, language: Language) -> str:
        """Replace number and unit withing given part of sentence.

        In the given part of the sentence the number and unit is replaced
        for another ones (given as a parameters).

        Numbers are rounded and scaling words are added when necessary.

        It has support for original translated number was a number modifier.

        :param sentence: Sentence to be replaced in
        :param source_number_unit: NumberUnit part from the source sentence
        :param target_number_unit: NumberUnit part from the target sentence
        :param new_number: Number to be replaced with
        :param new_unit: Unit to be replaced with
        :param language: Language of the sentence to be replaced in
        :return: Sentence with replaced wrong number
        """
        new_number = Replacer.__round_to_valid_digits(source_number_unit.number, new_number)
        new_number, used_scaling = Replacer.__add_scaling_word(source_number_unit, target_number_unit, new_number, language)

        if new_unit.before_number:
            replacement = new_unit.word + (" " if len(new_unit.word) > 1 else "") + str(new_number)

        elif target_number_unit.modifier:
            singular_unit = units.get_correct_unit(Languages.EN, 1, source_number_unit.unit, strict_category=new_unit.category, modifier=True)
            replacement = str(new_number) + "-" + singular_unit.word

        else:
            replacement = str(new_number) + " " + new_unit.word

        return sentence.replace(target_number_unit.text_part, replacement)

    @staticmethod
    def __round_to_valid_digits(original_number: Number, new_number: Number) -> Number:
        """Round the given number to specific count of valid digits

        Valid digits are all digits except zeros and the end of the number.

        Methods round up numbers to n+1 valid digits, where n is count of valid
        digits of original number.

        Example:
            45 124 000 has 5 valid digits
            From round up number 123 456 789 123 to 6 valid digits, so => 123 457 000 000

        :param original_number: Number to find out count of valid digits of
        :param new_number: Number to be rounded up
        :return: Rounded number
        """
        if original_number == new_number:
            return new_number

        # Find out count of valid digits
        valid_digits = sum([ch.isdigit() for ch in str(original_number)])
        for ch in reversed(str(original_number)):
            if ch.isdigit() and ch == '0':
                valid_digits -= 1
            elif ch.isdigit():
                valid_digits += 1
                break

        if isinstance(new_number, int):
            before_point = sum([ch.isdigit() for ch in str(new_number)])
        else:
            before_point, after_point = [len(part) for part in str(new_number).split('.')]

        if valid_digits <= before_point:
            return int(round(new_number, -(before_point - valid_digits)))
        else:
            return round(new_number, valid_digits - before_point)

    @staticmethod
    def __add_scaling_word(source_number_unit: NumberUnitFinderResult, target_number_unit: NumberUnitFinderResult, new_number: Number, language: Language) -> Tuple[str, bool]:
        """Add scaling word if there can be one.

        It decides based on the new number if there should be same scaling word
        and which specific it should be. It is decided based on validity rules declared
        within the list of scaling words.

        As a scaling word is selected that one, which value is last smaller value than the new number.

        When the number is same as in the source sentence, the scaling level from source
        sentence is used.

        Number is edited to be displayed with separators used in given language.

        :param source_number_unit: NumberUnit part from the source sentence
        :param target_number_unit: NumberUnit part from the target sentence
        :param new_number: Number to scaling word adding to
        :param language: Language of the sentence to be replaced in
        :return: Sentence with replaced wrong number
        """
        if not source_number_unit.scaling and not target_number_unit.scaling:
            return str(Replacer.__construct_right_form_of_number(language, new_number)), False

        last_possible_scaling = None
        for word, scaling_tuple in language.big_numbers_scale.items():
            if scaling_tuple[0] < new_number:
                last_possible_scaling = scaling_tuple[0]

        if new_number == source_number_unit.number and source_number_unit.scaling:
            last_possible_scaling = source_number_unit.scaling

        if not last_possible_scaling:
            return str(Replacer.__construct_right_form_of_number(language, new_number)), False

        divided = new_number / last_possible_scaling
        divided = int(divided) if divided.is_integer() else divided

        word = Replacer.__find_correct_scaling_word(last_possible_scaling, divided, language)
        if not word:
            return str(Replacer.__construct_right_form_of_number(language, new_number)), False

        return str(Replacer.__construct_right_form_of_number(language, divided)) + " " + word, True

    @staticmethod
    def __find_correct_scaling_word(scaling_number: int, number: Number, language: Language) -> Optional[str]:
        """Find best scaling word based on rules defined in scaling word list"""

        for word, scaling_tuple in {k: v for k, v in language.big_numbers_scale.items() if v[0] == scaling_number}.items():
            condition = scaling_tuple[1]

            if condition == None:  # Word cannot be used for replacing
                continue

            if condition == []:  # Word can be used for all numbers
                return word

            if isinstance(number, float) and float in condition:  # Word can be used for all float numbers
                return word

            if number in condition:  # Number is specified concretely
                return word

            for interval in [interval for interval in condition if isinstance(interval, tuple)]:  # Number is within a range
                left, right = interval
                if left is None and right is not None and number < right:
                    return word
                elif left is not None and right is None and number > left:
                    return word
                elif left is not None and right is not None and left < number < right:
                    return word

        return None

    @staticmethod
    def __construct_right_form_of_number(language: Language, number: Number) -> str:
        """Edit number to use separators based on given language"""
        string_number = str(number)
        parts = string_number.split(".")
        before_dot = parts[0]
        index = len(before_dot) - 1
        digits_count = 0
        result = []

        thousands_separator = " " if language == Languages.CS else ","

        while index >= 0:
            if digits_count == 3:
                result.append(thousands_separator)
                digits_count = 0

            result.append(before_dot[index])
            index -= 1
            digits_count += 1

        before_dot = "".join(reversed(result))

        if len(parts) > 1:
            return before_dot + language.decimal_separator + parts[1]
        else:
            return before_dot
