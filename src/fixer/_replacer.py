from ._custom_types import *
from ._finder import NumberUnitFinderResult
from ._languages import Language, Languages
from ._units import Unit, units


class Replacer:
    """Supporting class for replacing strings in broken sentences

    The class contains static methods for specific replacement algorithms.
    """

    @staticmethod
    def replace_unit(sentence: str, number_unit_part: str, number: Number, unit: Unit, new_unit: Unit, language, modifier=False, scaling=False) -> str:
        """Replace only unit within the broken sentence

        Based on new unit it decides whenever the unit should be put. When the new unit
        has flag "before number", the replacer returns unit before number.

        For units before number with length 1 there is no space between unit and number.
        For units after number there is number is first letter of unit is alphabet char.
        """

        translated_number = number_unit_part.replace(unit.word, "").strip(' ,-')

        # if new_unit.before_number and scaling:
        #    non_abbreviation_unit = units.get_correct_unit(language, number, unit, new_unit, new_unit.category, abbreviation=False)
        #    new_number_unit_part = f"{translated_number} {non_abbreviation_unit.word}"
        if new_unit.before_number and len(new_unit.word) == 1:
            new_number_unit_part = f"{new_unit.word}{translated_number}"
        elif new_unit.before_number:
            new_number_unit_part = f"{new_unit.word} {translated_number}"
        elif modifier and new_unit.language.acronym == Languages.EN.acronym:
            singular_unit = units.get_correct_unit(Languages.EN, 1, unit, new_unit, new_unit.category, modifier=True)
            new_number_unit_part = f"{translated_number}-{singular_unit.word}"
        elif not new_unit.word[0].isalpha():
            new_number_unit_part = f"{translated_number}{new_unit.word}"
        else:
            new_number_unit_part = f"{translated_number} {new_unit.word}"

        return sentence.replace(number_unit_part.strip(), new_number_unit_part).replace("  ", " ")

    @staticmethod
    def replace_number(sentence: str, source_number_unit: NumberUnitFinderResult, target_number_unit: NumberUnitFinderResult, language: Language, original_target_number: str, new_number: Number) -> str:

        new_number = Replacer.__round_to_valid_digits(source_number_unit.number, new_number)
        new_number, _ = Replacer.__add_scaling_word(target_number_unit, new_number, language)

        with_new_number = target_number_unit.text_part.replace(original_target_number, new_number)
        return sentence.replace(target_number_unit.text_part, with_new_number)

    @staticmethod
    def replace_unit_number(sentence: str, original_number_unit: NumberUnitFinderResult, src_number: Number, new_number: Number, new_unit: Unit, language: Language, *, modifier=False) -> str:
        new_number = Replacer.__round_to_valid_digits(src_number, new_number)
        new_number, used_scaling = Replacer.__add_scaling_word(original_number_unit, new_number, language)

        if new_unit.before_number:  # and not used_scaling:
            replacement = new_unit.word + (" " if len(new_unit.word) > 1 else "") + str(new_number)
        # elif new_unit.before_number:
        #    non_abbreviation_unit = units.get_correct_unit(language, new_number, original_number_unit.unit, new_unit, new_unit.category, abbreviation=False)
        #    replacement = new_number + " " + non_abbreviation_unit.word
        elif modifier:
            singular_unit = units.get_correct_unit(Languages.EN, 1, original_number_unit.unit, new_unit, new_unit.category, modifier=True)
            replacement = str(new_number) + "-" + singular_unit.word
        else:
            replacement = str(new_number) + " " + new_unit.word

        return sentence.replace(original_number_unit.text_part, replacement)

    @staticmethod
    def __round_to_valid_digits(original_number: Number, new_number: Number):
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
    def __add_scaling_word(original_number: NumberUnitFinderResult, new_number: Number, language: Language):
        #if not original_number.scaling:
        #    return str(new_number), False
        # TODO: Smarter deciding

        last_possible_scaling = None
        for word, scaling_tuple in language.big_numbers_scale.items():
            if scaling_tuple[0] < new_number:
                last_possible_scaling = scaling_tuple[0]

        if not last_possible_scaling:
            return str(new_number), False

        divided = new_number / last_possible_scaling
        divided = int(divided) if divided.is_integer() else divided

        word = Replacer.__find_correct_scaling_word(last_possible_scaling, divided, language)
        if not word:
            return str(new_number), False

        return str(divided) + " " + word, True

    @staticmethod
    def __find_correct_scaling_word(scaling_number, number, language):
        for word, scaling_tuple in {k: v for k, v in language.big_numbers_scale.items() if v[0] == scaling_number}.items():
            condition = scaling_tuple[1]

            if condition == None:
                continue

            if condition == []:
                return word

            if isinstance(number, float) and float in condition:
                return word

            if number in condition:
                return word

            for interval in [interval for interval in condition if isinstance(interval, tuple)]:
                left, right = interval
                if left is None and right is not None and number < right:
                    return word
                elif left is not None and right is None and number > left:
                    return word
                elif left is not None and right is not None and left < number < right:
                    return word

        return None

    @staticmethod
    def construct_right_form_of_number(language: Language, number: Number) -> str:
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
