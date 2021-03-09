from enum import Enum
from typing import Union, Optional, List

from _languages import Language, Languages


class UnitCategory(Enum):
    KMH = 0
    MS = 1
    M2 = 2
    KM2 = 3
    M3 = 4
    KM = 5
    M = 6
    DM = 7
    CM = 8
    MM = 9
    G = 10
    KG = 11
    LB = 12


class UnitDialect(Enum):
    BrE = 0  # British english
    AmE = 1  # American english


class Unit:

    def __init__(self,
                 word: str,
                 category: UnitCategory,
                 language: Language,
                 numbers_validity: Optional[List[Union[int, tuple, object]]],
                 recalculators: list,
                 abbreviation: bool,
                 dialect: Optional[UnitDialect]):
        self.word = word
        self.category = category
        self.language = language
        self.numbers_validity = numbers_validity
        self.recalculators = recalculators
        self.abbreviation = abbreviation

        if dialect:
            self.dialect = dialect
        else:
            self.dialect = None

    @staticmethod
    def number_pass_numbers_validity(validity: List, number: Union[int, float]) -> bool:
        if isinstance(number, float):
            if float in validity:
                return True
            else:
                return False

        if number in validity:
            return True

        for interval in validity:
            if not isinstance(interval, tuple):
                continue

            left, right = interval
            if left is None and right is not None and number < right:
                return True
            elif left is not None and right is None and number > left:
                return True
            elif left is not None and right is not None and left < number < right:
                return True

        return False


class UnitsWrapper:

    def __init__(self):
        self.__units = []
        self.__units_by_languages = {}

    def add_unit(self, unit: Unit):
        self.__units.append(unit)

    def get_correct_unit(self, language: Language, number: Union[float, int], original_unit: Unit, replacement_for: Unit):
        options_list = []
        for unit in self.__units:
            if unit.language != language or unit.category != original_unit.category:
                continue

            score = 0

            if unit.dialect == replacement_for.dialect:
                score += 1

            if unit.abbreviation == original_unit.abbreviation:
                score += 1

            if unit.numbers_validity is None:
                score += 1
            elif Unit.number_pass_numbers_validity(unit.numbers_validity, number):
                score += 2

            options_list.append((score, unit))

        options_list.sort(key=lambda tup: tup[0], reverse=True)
        return options_list[0][1]

    def get_words_by_category_language(self, category: int, language: Language) -> List[str]:
        words = []
        for unit in self.__units:
            if unit.category == category and unit.language == language:
                words.append(unit.word)

        return words

    def get_unit_by_word(self, word: str, language: Language) -> Optional[Unit]:
        for unit in self.__units:
            if unit.language == language and unit.word == word:
                return unit

        return None

    def get_regex_units_for_language(self, language: Language) -> str:
        units_for_language = self.get_all_units_for_language(language)

        return '|'.join([unit.word for unit in units_for_language])

    def get_all_units_for_language(self, language: Language) -> List[Unit]:
        if language not in self.__units_by_languages.keys():
            self.__units_by_languages[language] = []
            for unit in self.__units:
                if unit.language == language:
                    self.__units_by_languages[language].append(unit)

        return self.__units_by_languages[language]


numbers_validity_ones = [-1, 1]
numbers_validity_not_ones = [(None, -1), (1, None)]
numbers_validity_2_3_4 = [-4, -3, -2, 2, 3, 4]
numbers_validity_more_than_5 = [(None, -4), (4, None)]
numbers_validity_decimal = [float]

units = UnitsWrapper()

units.add_unit(Unit('km/h', UnitCategory.KMH, Languages.CS, None, [], True, None))
units.add_unit(Unit('kph', UnitCategory.KMH, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilometr za hodinu', UnitCategory.KMH, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry za hodinu', UnitCategory.KMH, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů za hodinu', UnitCategory.KMH, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometru za hodinu', UnitCategory.KMH, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometru v hodině', UnitCategory.KMH, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometrů v hodině', UnitCategory.KMH, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometr v hodině', UnitCategory.KMH, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry v hodině', UnitCategory.KMH, Languages.CS, numbers_validity_2_3_4, [], False, None))

units.add_unit(Unit('km/h', UnitCategory.KMH, Languages.EN, None, [], True, None))
units.add_unit(Unit('kph', UnitCategory.KMH, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilometers per hour', UnitCategory.KMH, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer per hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre per hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometres per hour', UnitCategory.KMH, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilometres an hour', UnitCategory.KMH, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilometers an hour', UnitCategory.KMH, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer an hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre an hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometer-an-hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre-an-hour', UnitCategory.KMH, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('m/s', UnitCategory.MS, Languages.CS, None, [], True, None))
units.add_unit(Unit('mps', UnitCategory.MS, Languages.CS, None, [], True, None))
units.add_unit(Unit('metr za sekundu', UnitCategory.MS, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metry za sekundu', UnitCategory.MS, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů za sekundu', UnitCategory.MS, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('metru za sekundu', UnitCategory.MS, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('m/s', UnitCategory.MS, Languages.EN, None, [], True, None))
units.add_unit(Unit('mps', UnitCategory.MS, Languages.EN, None, [], True, None))
units.add_unit(Unit('meters per second', UnitCategory.MS, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('meter per second', UnitCategory.MS, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('metres per second', UnitCategory.MS, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('metre per second', UnitCategory.MS, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('metr čtvereční', UnitCategory.M2, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metru čtverečního', UnitCategory.M2, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('metry čtvereční', UnitCategory.M2, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů čtverečních', UnitCategory.M2, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('square meter', UnitCategory.M2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square meters', UnitCategory.M2, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square metre', UnitCategory.M2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square metres', UnitCategory.M2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-metre', UnitCategory.M2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-meter', UnitCategory.M2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))

units.add_unit(Unit('kilometr čtvereční', UnitCategory.KM2, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometru čtverečního', UnitCategory.KM2, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometry čtvereční', UnitCategory.KM2, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů čtverečních', UnitCategory.KM2, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('square kilometer', UnitCategory.KM2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square kilometers', UnitCategory.KM2, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square kilometre', UnitCategory.KM2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square kilometres', UnitCategory.KM2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-kilometre', UnitCategory.KM2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-kilometer', UnitCategory.KM2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))

units.add_unit(Unit('metr krychlový', UnitCategory.M3, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metru krychlového', UnitCategory.M3, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('metry krychlové', UnitCategory.M3, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů krychlových', UnitCategory.M3, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('cubic meter', UnitCategory.M3, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('cubic meters', UnitCategory.M3, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('cubic metre', UnitCategory.M3, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('cubic metres', UnitCategory.M3, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('km', UnitCategory.KM, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilometr', UnitCategory.KM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry', UnitCategory.KM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů', UnitCategory.KM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometru', UnitCategory.KM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('km', UnitCategory.KM, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilometers', UnitCategory.KM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer', UnitCategory.KM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre', UnitCategory.KM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometres', UnitCategory.KM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('m', UnitCategory.M, Languages.CS, None, [], True, None))
units.add_unit(Unit('metr', UnitCategory.M, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metry', UnitCategory.M, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů', UnitCategory.M, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('metru', UnitCategory.M, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('m', UnitCategory.M, Languages.EN, None, [], True, None))
units.add_unit(Unit('meters', UnitCategory.M, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('meter', UnitCategory.M, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('metre', UnitCategory.M, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metres', UnitCategory.M, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('dm', UnitCategory.DM, Languages.CS, None, [], True, None))
units.add_unit(Unit('decimetr', UnitCategory.DM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('decimetry', UnitCategory.DM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('decimetrů', UnitCategory.DM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('decimetru', UnitCategory.DM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('dm', UnitCategory.DM, Languages.EN, None, [], True, None))
units.add_unit(Unit('decimeters', UnitCategory.DM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('decimeter', UnitCategory.DM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('decimetre', UnitCategory.DM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('decimetres', UnitCategory.DM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('cm', UnitCategory.CM, Languages.CS, None, [], True, None))
units.add_unit(Unit('centimetr', UnitCategory.CM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('centimetry', UnitCategory.CM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('centimetrů', UnitCategory.CM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('centimetru', UnitCategory.CM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('cm', UnitCategory.CM, Languages.EN, None, [], True, None))
units.add_unit(Unit('centimeters', UnitCategory.CM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('centimeter', UnitCategory.CM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('centimetre', UnitCategory.CM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('centimetres', UnitCategory.CM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('mm', UnitCategory.MM, Languages.CS, None, [], True, None))
units.add_unit(Unit('milimetr', UnitCategory.MM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('milimetry', UnitCategory.MM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('milimetrů', UnitCategory.MM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('milimetru', UnitCategory.MM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('mm', UnitCategory.MM, Languages.EN, None, [], True, None))
units.add_unit(Unit('millimeters', UnitCategory.MM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('millimeter', UnitCategory.MM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('milimetre', UnitCategory.MM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('millimetre', UnitCategory.MM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('milimetres', UnitCategory.MM, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('millimetres', UnitCategory.MM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('g', UnitCategory.G, Languages.CS, None, [], True, None))
units.add_unit(Unit('gram', UnitCategory.G, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('gramy', UnitCategory.G, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('gramů', UnitCategory.G, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('gramu', UnitCategory.G, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('g', UnitCategory.G, Languages.EN, None, [], True, None))
units.add_unit(Unit('grams', UnitCategory.G, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('gram', UnitCategory.G, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('kg', UnitCategory.KG, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilogram', UnitCategory.KG, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilogramy', UnitCategory.KG, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilogramů', UnitCategory.KG, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilogramu', UnitCategory.KG, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kila', UnitCategory.KG, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilo', UnitCategory.KG, Languages.CS, [(None, -4), -1, 1, (4, None)], [], False, None))
units.add_unit(Unit('kil', UnitCategory.KG, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('kg', UnitCategory.KG, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilograms', UnitCategory.KG, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilogram', UnitCategory.KG, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilos', UnitCategory.KG, Languages.EN, numbers_validity_not_ones, [], False, None))

# IMPERIAL
units.add_unit(Unit('pounds', UnitCategory.LB, Languages.EN, numbers_validity_not_ones, [], False, None))

"""
units = {
    'km/h': {
        'cs': ['km/h', 'kph', 'kilometr za hodinu', 'kilometry za hodinu', 'kilometrů za hodinu', 'kilometrů v hodině',
               'kilometr v hodině', 'kilometry v hodině'],
        'en': ['km/h', 'kph', 'kilometers per hour', 'kilometer per hour', 'kilometres per hour', 'kilometres an hour',
               'kilometers an hour', 'kilometer-an-hour']},
    'm/s': {
        'cs': ['m/s', 'mps', 'metr za sekundu', 'metry za sekundu', 'metrů za sekundu', 'metru za sekundu'],
        'en': ['m/s', 'mps', 'meters per second', 'meter per second']},
    'm2': {
        'cs': ['metr čtvereční', 'metru čtverečního', 'metry čtvereční', 'metrů čtverečních'],
        'en': ['square meter', 'square meters', 'square metre', 'square metres', 'square-metre', 'square-meter']},
    'km2': {
        'cs': ['kilometr čtvereční', 'kilometru čtverečního', 'kilometry čtvereční', 'kilometrů čtverečních'],
        'en': ['square kilometer', 'square kilometers', 'square kilometre', 'square kilometres', 'square-kilometre',
               'square-kilometer']},
    'm3': {
        'cs': ['metr krychlový', 'metru krychlového', 'metry krychlové', 'metrů krychlových'],
        'en': ['cubic meter', 'cubic meters', 'cubic metre', 'cubic metres']},
    'km': {
        'cs': ['km', 'kilometr', 'kilometry', 'kilometrů', 'kilometru'],
        'en': ['km', 'kilometers', 'kilometer', 'kilometre', 'kilometres']},
    'm': {
        'cs': ['m', 'metr', 'metry', 'metrů', 'metru'],
        'en': ['m', 'meters', 'meter', 'metre', 'metres']},
    'dm': {
        'cs': ['dm', 'decimetr', 'decimetry', 'decimetrů'],
        'en': ['dm', 'decimeters', 'decimeter', 'metre', 'metres']},
    'cm': {
        'cs': ['cm', 'centimetr', 'centimetry', 'centimetrů'],
        'en': ['cm', 'centimeters', 'centimeter', 'centimetre', 'centimetre', 'centimetres']},
    'mm': {
        'cs': ['mm', 'milimetr', 'milimetry', 'milimetrů'],
        'en': ['mm', 'millimeters', 'millimeter', 'milimetre', 'millimetre', 'milimetres', 'millimetres']},
    'g': {
        'cs': ['g', 'gram', 'gramy', 'gramů'],
        'en': ['g', 'grams', 'gram']},
    'kg': {
        'cs': ['kg', 'kilogram', 'kilogramy', 'kilogramů', 'kila', 'kilo', 'kil'],
        'en': ['kg', 'kilograms', 'kilogram', 'kilos']},
}


if __name__ == "__main__":
    for idx, category in enumerate(units.keys()):
        category_upper = category.replace('/', '').upper()
        print(f"{category_upper} = {idx}")

        
        for language, language_values in category_values.items():
            language_parsed = Languages.CS if language == 'cs' else Languages.EN

            for unit in language_values:
                abbrevation = True if len(unit) <= 2 else False

                print(f"units.add_unit(Unit('{unit}', UnitCategory.{category_upper}, {language_parsed}, None, [], {abbrevation}, None))")


units_by_language = {}
for _, val in units.items():
    for lang, u in val.items():
        if lang not in units_by_language.keys():
            units_by_language[lang] = []

        units_by_language[lang] += u

units_strings = {lang: '|'.join(units_list) for lang, units_list in units_by_language.items()}

units_categories = {}
for category, val in units.items():
    for lang, lang_list in val.items():
        if lang not in units_categories.keys():
            units_categories[lang] = {}

        for unit in lang_list:
            units_categories[lang][unit] = category
"""
"""
lenght_units = {
    'si': (
        ['m', 'mm', 'cm', 'dm', 'km'],
        [1, 0.001, 0.01, 0.1, 1000]
    ),
    'imperial': (
        ['in', 'ft', 'yd', 'miles'],
        [1, 12, 36, 63360]
    ),
    'si-imp': 39.37007874,
    'imp-si': 0.0254
}


def convert_to_specific(number, rest, source, rate, target):
    idx = source[0].index(rest)
    number_in_base = number * source[1][idx]

    base_in_second = number_in_base * rate
    for i in range(len(target[0]) - 1, -1, -1):
        calc = base_in_second / target[1][i]
        if calc >= 1:
            return calc, target[0][i]

    return base_in_second, target[0][0]


def convert_unit(number: int, rest: str):
    if rest in lenght_units['si'][0]:
        number, rest = convert_to_specific(number, rest, lenght_units['si'], lenght_units['si-imp'],
                                           lenght_units['imperial'])
    elif rest in lenght_units['imperial'][0]:
        number, rest = convert_to_specific(number, rest, lenght_units['imperial'], lenght_units['imp-si'],
                                           lenght_units['si'])

    return number, rest
"""
