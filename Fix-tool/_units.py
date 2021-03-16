from enum import Enum
from typing import Union, Optional, List

from _languages import Language, Languages


class UnitsSystem(Enum):
    SI = 0
    Imperial = 1
    USCustomary = 2


class UnitCategory:

    def __init__(self, system: List[UnitsSystem], base, base_coefficient: Optional[float], *, conversion=None):
        self.system = system
        self.base = base
        self.base_coefficient = base_coefficient
        self.conversion = conversion


class UnitCategories:
    MS = UnitCategory([UnitsSystem.SI], None, None)
    KMH = UnitCategory([UnitsSystem.SI], MS, 1000 / 3600)
    M2 = UnitCategory([UnitsSystem.SI], None, None)
    KM2 = UnitCategory([UnitsSystem.SI], M2, 1000000)
    M3 = UnitCategory([UnitsSystem.SI], None, None)
    M = UnitCategory([UnitsSystem.SI], None, None)
    KM = UnitCategory([UnitsSystem.SI], M, 1000)
    DM = UnitCategory([UnitsSystem.SI], M, 0.1)
    CM = UnitCategory([UnitsSystem.SI], M, 0.01)
    MM = UnitCategory([UnitsSystem.SI], M, 0.001)
    G = UnitCategory([UnitsSystem.SI], None, None)
    KG = UnitCategory([UnitsSystem.SI], G, 1000)
    LB = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], None, None)
    FT = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], None, None)
    IN = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], FT, 1 / 12)
    YD = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], FT, 3)
    MI = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], FT, 5280)
    FT2 = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], None, None)
    MI2 = UnitCategory([UnitsSystem.Imperial, UnitsSystem.USCustomary], FT2, 1 / 27878400)

    # TODO: Add converting methods
"""
    def __init__(self):
        self.categories_groups = {}

        all_categories = [a for a in dir(UnitCategories) if not a.startswith('__')]
        for category in all_categories:
            category_object = getattr(UnitCategories, category)
            if category_object.base is None:
                self.categories_groups[category_object] = []
            else:
                if category_object.base not in self.categories_groups.keys():
                    self.categories_groups[category_object.base] = []

                self.categories_groups[category_object.base].append(category_object)

    @staticmethod
    def weight_conversion(number: Union[float, int], original_category: UnitCategory):
        base = number
        if original_category.base is None:
            base = number * original_category.base_coefficient

        if original_category.system == UnitsSystem.SI:
            target = base * (1 / 453.59237)
        else:
            target = base * 453.59237

units_categories = UnitCategories()
"""

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


"""
class UnitsRecalculator(ABC):

    @staticmethod
    def recalculate(original_unit: Unit, translated_unit: Unit, original_number: Union[int, float]):
        pass


class WeightRecalculator(UnitsRecalculator):
    si_recalculations = {
        UnitCategory.G: 1,
        UnitCategory.KG: 1000,
    }

    imperial_recalculations = {
        UnitCategory.LB: 1,
    }

    default_metric = UnitCategory.G
    default_imperial = UnitCategory.LB

    @staticmethod
    def recalculate(original_unit: Unit, translated_unit: Unit, original_number: Union[int, float]):
        if original_unit.category !=
"""

numbers_validity_ones = [-1, 1]
numbers_validity_not_ones = [(None, -1), (1, None)]
numbers_validity_2_3_4 = [-4, -3, -2, 2, 3, 4]
numbers_validity_more_than_5 = [(None, -4), (4, None)]
numbers_validity_decimal = [float]

units = UnitsWrapper()

units.add_unit(Unit('km/h', UnitCategories.KMH, Languages.CS, None, [], True, None))
units.add_unit(Unit('kph', UnitCategories.KMH, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilometr za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometru za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometru v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometrů v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometr v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_2_3_4, [], False, None))

units.add_unit(Unit('km/h', UnitCategories.KMH, Languages.EN, None, [], True, None))
units.add_unit(Unit('kph', UnitCategories.KMH, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilometers per hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer per hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre per hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometres per hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilometres an hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilometers an hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer an hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre an hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometer-an-hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre-an-hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('m/s', UnitCategories.MS, Languages.CS, None, [], True, None))
units.add_unit(Unit('mps', UnitCategories.MS, Languages.CS, None, [], True, None))
units.add_unit(Unit('metr za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metry za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('metru za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('m/s', UnitCategories.MS, Languages.EN, None, [], True, None))
units.add_unit(Unit('mps', UnitCategories.MS, Languages.EN, None, [], True, None))
units.add_unit(Unit('meters per second', UnitCategories.MS, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('meter per second', UnitCategories.MS, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('metres per second', UnitCategories.MS, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('metre per second', UnitCategories.MS, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('metr čtvereční', UnitCategories.M2, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metru čtverečního', UnitCategories.M2, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('metry čtvereční', UnitCategories.M2, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů čtverečních', UnitCategories.M2, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('square meter', UnitCategories.M2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square meters', UnitCategories.M2, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square metre', UnitCategories.M2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square metres', UnitCategories.M2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-metre', UnitCategories.M2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-meter', UnitCategories.M2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))

units.add_unit(Unit('kilometr čtvereční', UnitCategories.KM2, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometru čtverečního', UnitCategories.KM2, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kilometry čtvereční', UnitCategories.KM2, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů čtverečních', UnitCategories.KM2, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('square kilometer', UnitCategories.KM2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square kilometers', UnitCategories.KM2, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('square kilometre', UnitCategories.KM2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square kilometres', UnitCategories.KM2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-kilometre', UnitCategories.KM2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-kilometer', UnitCategories.KM2, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))

units.add_unit(Unit('metr krychlový', UnitCategories.M3, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metru krychlového', UnitCategories.M3, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('metry krychlové', UnitCategories.M3, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů krychlových', UnitCategories.M3, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('cubic meter', UnitCategories.M3, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('cubic meters', UnitCategories.M3, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('cubic metre', UnitCategories.M3, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('cubic metres', UnitCategories.M3, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('km', UnitCategories.KM, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilometr', UnitCategories.KM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometry', UnitCategories.KM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilometrů', UnitCategories.KM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilometru', UnitCategories.KM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('km', UnitCategories.KM, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilometers', UnitCategories.KM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometer', UnitCategories.KM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('kilometre', UnitCategories.KM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilometres', UnitCategories.KM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('m', UnitCategories.M, Languages.CS, None, [], True, None))
units.add_unit(Unit('metr', UnitCategories.M, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metry', UnitCategories.M, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('metrů', UnitCategories.M, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('metru', UnitCategories.M, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('m', UnitCategories.M, Languages.EN, None, [], True, None))
units.add_unit(Unit('meters', UnitCategories.M, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('meter', UnitCategories.M, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('metre', UnitCategories.M, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('metres', UnitCategories.M, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('dm', UnitCategories.DM, Languages.CS, None, [], True, None))
units.add_unit(Unit('decimetr', UnitCategories.DM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('decimetry', UnitCategories.DM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('decimetrů', UnitCategories.DM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('decimetru', UnitCategories.DM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('dm', UnitCategories.DM, Languages.EN, None, [], True, None))
units.add_unit(Unit('decimeters', UnitCategories.DM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('decimeter', UnitCategories.DM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('decimetre', UnitCategories.DM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('decimetres', UnitCategories.DM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('cm', UnitCategories.CM, Languages.CS, None, [], True, None))
units.add_unit(Unit('centimetr', UnitCategories.CM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('centimetry', UnitCategories.CM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('centimetrů', UnitCategories.CM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('centimetru', UnitCategories.CM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('cm', UnitCategories.CM, Languages.EN, None, [], True, None))
units.add_unit(Unit('centimeters', UnitCategories.CM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('centimeter', UnitCategories.CM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('centimetre', UnitCategories.CM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('centimetres', UnitCategories.CM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('mm', UnitCategories.MM, Languages.CS, None, [], True, None))
units.add_unit(Unit('milimetr', UnitCategories.MM, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('milimetry', UnitCategories.MM, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('milimetrů', UnitCategories.MM, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('milimetru', UnitCategories.MM, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('mm', UnitCategories.MM, Languages.EN, None, [], True, None))
units.add_unit(Unit('millimeters', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('millimeter', UnitCategories.MM, Languages.EN, numbers_validity_ones, [], False, UnitDialect.AmE))
units.add_unit(Unit('milimetre', UnitCategories.MM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('millimetre', UnitCategories.MM, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('milimetres', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('millimetres', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('g', UnitCategories.G, Languages.CS, None, [], True, None))
units.add_unit(Unit('gram', UnitCategories.G, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('gramy', UnitCategories.G, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('gramů', UnitCategories.G, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('gramu', UnitCategories.G, Languages.CS, numbers_validity_decimal, [], False, None))

units.add_unit(Unit('g', UnitCategories.G, Languages.EN, None, [], True, None))
units.add_unit(Unit('grams', UnitCategories.G, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('gram', UnitCategories.G, Languages.EN, numbers_validity_ones, [], False, None))

units.add_unit(Unit('kg', UnitCategories.KG, Languages.CS, None, [], True, None))
units.add_unit(Unit('kilogram', UnitCategories.KG, Languages.CS, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilogramy', UnitCategories.KG, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilogramů', UnitCategories.KG, Languages.CS, numbers_validity_more_than_5, [], False, None))
units.add_unit(Unit('kilogramu', UnitCategories.KG, Languages.CS, numbers_validity_decimal, [], False, None))
units.add_unit(Unit('kila', UnitCategories.KG, Languages.CS, numbers_validity_2_3_4, [], False, None))
units.add_unit(Unit('kilo', UnitCategories.KG, Languages.CS, [(None, -4), -1, 1, (4, None)], [], False, None))
units.add_unit(Unit('kil', UnitCategories.KG, Languages.CS, numbers_validity_more_than_5, [], False, None))

units.add_unit(Unit('kg', UnitCategories.KG, Languages.EN, None, [], True, None))
units.add_unit(Unit('kilograms', UnitCategories.KG, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('kilogram', UnitCategories.KG, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('kilos', UnitCategories.KG, Languages.EN, numbers_validity_not_ones, [], False, None))

# IMPERIAL
# units.add_unit(Unit('in', UnitCategories.IN, Languages.EN, None, [], True, None))
units.add_unit(Unit('inch', UnitCategories.IN, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('inches', UnitCategories.IN, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('square foot', UnitCategories.FT2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-foot', UnitCategories.FT2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square feet', UnitCategories.FT2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-feet', UnitCategories.FT2, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('ft', UnitCategories.FT, Languages.EN, None, [], True, None))
units.add_unit(Unit('foot', UnitCategories.FT, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('feet', UnitCategories.FT, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('yd', UnitCategories.YD, Languages.EN, None, [], True, None))
units.add_unit(Unit('yard', UnitCategories.YD, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('yards', UnitCategories.YD, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('square mile', UnitCategories.MI2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square-mile', UnitCategories.MI2, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('square miles', UnitCategories.MI2, Languages.EN, numbers_validity_not_ones, [], False, None))
units.add_unit(Unit('square-miles', UnitCategories.MI2, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('mi', UnitCategories.MI, Languages.EN, None, [], True, None))
units.add_unit(Unit('mile', UnitCategories.MI, Languages.EN, numbers_validity_ones, [], False, None))
units.add_unit(Unit('miles', UnitCategories.MI, Languages.EN, numbers_validity_not_ones, [], False, None))

units.add_unit(Unit('pounds', UnitCategories.LB, Languages.EN, numbers_validity_not_ones, [], False, None))

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
