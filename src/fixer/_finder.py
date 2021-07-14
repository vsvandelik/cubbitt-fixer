import re
from typing import List, Optional, Dict

from fixer._words_to_numbers_converter import WordsNumbersConverter, WordsNumbersConverterException

from ._custom_types import *
from ._languages import Language, Languages
from ._units import Unit, units


class NumberUnitFinderResult:
    """Data class for saving parsed part of the sentence - numbers (with units)

    :ivar number: number value
    :ivar unit: instance of unit class
    :ivar approximately: flag whenever the number is approximate
    :ivar text_part: string containing number and unit as substring of original sentence
    :ivar scaling: number used as a scaling in original sentence (eg. 1000 when used thousands)
    :ivar number_as_string: text representation of the number (if there was in original sentence)
    :ivar modifier: flag whenever the number and unit was used as a number modifier

    :param number: Parsed number value
    :param unit: Instance of unit (can be None when there is no unit)
    :param approximately: Indicator if the value is approximate
    :param text_part: Substring of the sentence with the number (and unit)
    """

    def __init__(self, number: Number, unit: Optional[Unit], approximately: bool, text_part: str):
        self.number = number
        self.unit = unit
        self.approximately = approximately
        self.text_part = text_part
        self.scaling = None
        self.number_as_string = None
        self.modifier = False

    def add_scaling(self, scaling: int):
        """Set scaling to number, the number is multiplied by scaling constant."""
        self.scaling = scaling
        self.number *= scaling

    def set_number_as_string(self, word_number: str):
        """Saving the text representation of a number"""
        self.number_as_string = word_number


def prepare_find_numbers_pattern() -> Dict[Language, re.Pattern]:
    """Prepares regex patters for the finder"""
    return {
        Languages.CS: prepare_find_numbers_pattern_one_language(Languages.CS),
        Languages.EN: prepare_find_numbers_pattern_one_language(Languages.EN),
    }


def prepare_find_numbers_pattern_one_language(language: Language) -> re.Pattern:
    """Prepare regex patter based on given language"""
    units_before = units.get_regex_units_for_language_before_numbers(language)
    sep_thousands = re.escape(language.thousands_separator)
    sep_decimals = re.escape(language.decimal_separator)
    scales = language.big_numbers_scale_keys
    units_all = units.get_regex_units_for_language(language)

    return re.compile(r"(?:(?P<inches>(\d+\'\d+\")|(\d+-(?:foot|feet)-\d+))"
                      r"|(?P<skipping>(\d{1,2}\.\s?\d{1,2}\.\s?\d{4}?)|(\d+[-:]\d+))"
                      rf"|(?P<unit>{units_before})\s?(?P<number>\d+(?:[ {sep_thousands}]\d{{3}})*(?:{sep_decimals}\d+)?)[\s-]?(?:(?P<scaling>{scales}|m)\b)?"
                      rf"|(?P<a_number>\d+(?:[ {sep_thousands}]\d{{3}})*({sep_decimals}\d+)?)[\s-]?(?:(?P<a_scaling>{scales}|m)(?:\b[\s-]?|[\s-]))?(?P<a_unit>{units_all})?(?:\b|\s|$|[,.\s]))",
                      re.IGNORECASE)


class Finder:
    """Helping class wrapping methods for finding number (and units) parts in the sentence.

    The searching has two main parts - searching for the numbers written as digits and
    searching for the numbers written as text.
    """

    __FIND_NUMBERS_PATTERN = prepare_find_numbers_pattern()  #: :meta hide-value:

    @staticmethod
    def find_number_unit_pairs(sentence: str, language: Language) -> List[NumberUnitFinderResult]:
        """Search in sentence for number (and units) parts

        Based on regular expression the pairs of numbers and units are
        searched within the input sentence. Also the approximately
        phrases are searched.

        Non-parsable numbers are skipped.

        :param sentence: Sentence to search in
        :param language: Language of the sentence
        :return: List of found numbers
        """
        pairs = []
        for part in re.finditer(Finder.__FIND_NUMBERS_PATTERN[language], sentence):
            whole_match = part.group(0).strip(" .,-")

            if part.group("skipping"):
                continue

            if part.group("inches") and language == Languages.EN:  # Special behaviour for eg. 6'12"
                substring = part.group("inches")
                number = Finder.__convert_text_to_inches(substring)
                unit = units.get_unit_by_word("inch", Languages.EN)
                approximately = Finder.__find_approximately_phrase(language, substring, sentence)
                pairs.append(NumberUnitFinderResult(number, unit, approximately, substring))
                continue

            try:
                matched_number = Finder.__get_value_from_group_match(part, "number")
                matched_number = matched_number.replace(language.thousands_separator, "").replace(" ", "").replace(language.decimal_separator, ".")
                number = float(matched_number) if "." in matched_number else int(matched_number)
            except ValueError:  # skip if the number cannot be parsed
                continue

            approximately = Finder.__find_approximately_phrase(language, whole_match, sentence)
            scale_key = Finder.__get_value_from_group_match(part, "scaling")

            unit_string = Finder.__get_value_from_group_match(part, "unit")
            unit = units.get_unit_by_word(unit_string, language) if unit_string else None

            # unsure if it is the scaling "m" or the unit "m"
            if scale_key == "m" and not unit:
                continue

            # skip time and sport score (eg. 4:45 or 3-6)
            if re.search(f"{number}[-:]\\d+|\\d+[-:]{number}", sentence):
                continue

            pairs.append(NumberUnitFinderResult(number, unit, approximately, whole_match))

            if unit and '-' + unit.word in whole_match:
                pairs[-1].modifier = True

            if scale_key and scale_key == "m":
                pairs[-1].add_scaling(1000000)
            elif scale_key:
                pairs[-1].add_scaling(language.big_numbers_scale[scale_key.lower()][0])

        return pairs

    @staticmethod
    def find_word_number_unit(sentence: str, language: Language, sentence_analysis: List[dict]) -> List[NumberUnitFinderResult]:
        """Find numbers which has text representation in the sentence

        Using the sentence analysis provided by external tools as UDPipe the sentence is filtered
        for phrases containing numbers or scaling words (like thousands).

        Those phrases are parsed and text representation of the numbers is converted to the number.
        It can also searches for the unit near to found number phrase.

        Non-parsable numbers are skipped.

        :param sentence: Input sentence to be analysed
        :param language: Language of the input sentence
        :param sentence_analysis: Analysis of the sentence provided by tools such a UDPipe
        :return: List of found numbers
        """
        #  Do not find numbers when there is any word containing a number
        if not sentence_analysis or not any(word['upostag'] == 'NUM' and not word['word'][0].isdigit() for word in sentence_analysis):
            return []

        values = Finder.__filter_and_match_tokens_next_to_each_other_together(language, sentence_analysis)
        values = Finder.__split_siblings_numbers(values, language)
        found_number_units = []

        for phrase in values:
            # skip phrases containing only punctuation, digits and non number words
            if all(word['upostag'] == 'PUNCT' or word['word'][0].isdigit() or word['word'] == "and" or word['word'] == "a" for word in phrase):
                continue

            # skip phrases containing simple digits and scaling word (these were caught by digits finder)
            elif phrase[0]['word'][0].isdigit() and phrase[1]['lemma'] in language.big_numbers_scale.keys():
                continue

            # skip numbers with czech separators with scaling word (eg. 10,4 million)
            elif phrase[0]['word'][0].isdigit() and phrase[1]['upostag'] == "PUNCT" and phrase[2]['word'][0].isdigit() and phrase[3]['lemma'] in language.big_numbers_scale.keys():
                continue

            # find unit next to the number in phrase
            start = phrase[0]['rangeStart']
            end = phrase[-1]['rangeEnd']
            matched_unit = None
            whole_match = sentence[start:end]
            for unit in re.finditer(rf"\b({units.get_regex_units_for_language(language)})\b", sentence):
                if unit.group(0).strip() in units.get_units_for_language_before_numbers_list(language) and 0 <= (start - unit.end()) <= 2:
                    matched_unit = unit.group(0)
                    whole_match = sentence[unit.start():end]
                    break
                elif 0 <= (unit.start() - end) <= 2:
                    matched_unit = unit.group(0)
                    whole_match = sentence[start:unit.end()]
                    break

            if matched_unit:
                matched_unit = units.get_unit_by_word(matched_unit, language)

            approximately = Finder.__find_approximately_phrase(language, whole_match, sentence)

            # search for scaling word
            scaling_words = [word['word'] for word in phrase if word['word'].lower() in language.big_numbers_scale]
            scaling_word = scaling_words[0] if scaling_words else None

            # add article when english sentence
            if language == Languages.EN and f"a {re.escape(whole_match)}" in sentence:
                whole_match = f"a {whole_match}"
                start -= 2

            try:
                number = WordsNumbersConverter.convert([data['lemma'] for data in phrase if data['upostag'] != 'PUNCT'], language)
            except WordsNumbersConverterException:
                continue
            except ValueError:
                continue

            found_number_units.append(NumberUnitFinderResult(number, matched_unit, approximately, whole_match))
            found_number_units[-1].set_number_as_string(sentence[start:end + 1].strip(" -"))

            if matched_unit and '-' + matched_unit.word in whole_match:
                found_number_units[-1].modifier = True

            if scaling_word:
                found_number_units[-1].scaling = language.big_numbers_scale[scaling_word.lower()][0]

        return found_number_units

    @staticmethod
    def __get_value_from_group_match(match_object: re.Match, group_name: str) -> Optional[str]:
        """Returns value of regex match group by group name (when its empty, value of group name prefixed with 'a' is returned)"""
        if match_object.group(group_name):
            return match_object.group(group_name)
        elif match_object.group("a_" + group_name):
            return match_object.group("a_" + group_name)
        else:
            return None

    @staticmethod
    def __convert_text_to_inches(text: str) -> int:
        """Convert number written as feet and inches (6'12" or 6-feet-12) to inches"""

        if "feet" in text or "foot" in text:
            feet, _, inches = text.split("-")
        else:
            feet, inches = text.strip("\"").split("'")

        return int(inches) + 12 * int(feet)

    @staticmethod
    def __find_approximately_phrase(language: Language, match: str, sentence: str) -> bool:
        """Returns whenever before the found match is phrase indicating approximate (eg. cca, ...)"""
        return True if re.search(rf"({'|'.join(language.approximately_phrases)}) {re.escape(match)}", sentence) else False

    @staticmethod
    def __filter_and_match_tokens_next_to_each_other_together(language: Language, sentence_analysis: List[dict]) -> List[List[dict]]:
        """Process the sentence analysis and returns interesting phrases

        It finds in the sentence tokens containing number (and scaling words and punctuation)
        and concatenate tokens next to each other together.

        :param language: Language of the sentence
        :param sentence_analysis: Data from external tool such a UDPipe
        :return: List of phrases (tokens next to each others)
        """
        values = []
        current_phrase = []
        inside_number_phrase = False
        last_end = None

        def trim_and_add_to_values(phrase_to_add: List[dict]):
            """Trim punctuation at the end of phrase"""
            nonlocal values
            if phrase_to_add:
                while phrase_to_add[-1]['upostag'] == 'PUNCT' or phrase_to_add[-1]['word'] in ['and', 'a']:
                    phrase_to_add.pop()
                values.append(phrase_to_add)

        for data in sentence_analysis:

            # filter only specific tokens (numbers, scaling words, "and", "a", punctuation
            if data['upostag'] != 'NUM' and \
                    data['lemma'] not in language.big_numbers_scale.keys() and \
                    not (data['upostag'] == 'PUNCT' and inside_number_phrase) and \
                    not (data['word'] == 'and' and language.acronym == Languages.EN.acronym and inside_number_phrase) and \
                    not (data['word'] == 'a' and language.acronym == Languages.CS.acronym and inside_number_phrase):
                trim_and_add_to_values(current_phrase)  # if there was some phrase open, save it
                current_phrase = []
                inside_number_phrase = False
                continue

            inside_number_phrase = True

            if not current_phrase:
                current_phrase.append(data)
            elif data['rangeStart'] <= last_end + 1:  # if the token is strictly next token
                current_phrase.append(data)
            else:
                trim_and_add_to_values(current_phrase)
                current_phrase = [data]

            last_end = data['rangeEnd']

        trim_and_add_to_values(current_phrase)

        return values

    @staticmethod
    def __split_siblings_numbers(phrases: List[List[dict]], language: Language) -> List[List[dict]]:
        """Split numbers next to each other written without delimiter (eg. pět šest metrů)

        It supports also format with and delimiter (eg. five and six)

        :param phrases: List of found phrases
        :param language: Language of the sentence
        :return: Changed list of found phrases
        """
        to_remove = []
        to_add = []

        for idx, phrase in enumerate(phrases):
            if not (len(phrase) == 2 or (len(phrase) == 3 and phrase[1]['word'] in ['a', 'and'])):
                continue

            first = phrase[0]['lemma']
            last = phrase[-1]['lemma']

            words = WordsNumbersConverter.CS if language == Languages.CS else WordsNumbersConverter.EN
            first_num = words.get(first)
            last_num = words.get(last)

            if not first_num or not last_num:
                continue

            if 0 < first_num < last_num < 10 or 10 <= first_num < last_num < 100:
                to_remove.append(idx)
                to_add.append([phrase[0]])
                to_add.append([phrase[-1]])

        for removing in to_remove:
            phrases.pop(removing)

        return phrases + to_add
