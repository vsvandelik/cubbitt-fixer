import re
from enum import Enum, auto
from typing import Union, Optional, List, Tuple, Callable, Dict

from ._custom_types import Number
from ._exchange_rates import exchange_rates_convertor
from ._languages import Language, Languages


class UnitsSystem(Enum):
    """List of unit systems - groups of units"""
    SI = auto()  #: Basic SI units (meters, grams)
    IMPERIAL = auto()  #: Basic imperial units (inches, pounds)
    CZK = auto()  #: Czech crowns
    GBP = auto()  #: Great Britain Pounds
    USD = auto()  #: US dollars
    EUR = auto()  #: Euros
    C = auto()  #: Degree Celsius
    F = auto()  #: Degree Fahrenheit


class UnitDialect(Enum):
    """Dialect of the unit (british or american english) - NOT USED IN CODE"""
    BrE = 0  # British english
    AmE = 1  # American english


class UnitCategory:
    """Wrapper data class for single unit category

    As category is considered one single unit (different forms of unit words are still one category).

    :param system: System category belongs to
    :param base: Instance of another UnitCategory used as base (eg. meters are based for distance in SI)
    :type base: UnitCategory or None
    :param base_coefficient: Coefficient to convert from base category to this one
    :param conversion: Function to converts between different UnitSystems, only for base categories
    """

    def __init__(self, system: UnitsSystem, base, base_coefficient: Optional[float], *, conversion: Optional[Callable] = None):
        self.system = system
        self.base = base
        self.base_coefficient = base_coefficient
        self.conversion = conversion


class UnitsConvertors:
    """Wrapper for methods used for conversion between unit systems."""

    @staticmethod
    def get_best_unit_for_converted_number(number: Number, category: UnitCategory, language: Language, original_unit, translated_unit):
        """Find best unit category for given number

        Example
            Number was converted from inches to meters. In meters it is 2500 ->
            this method should convert the number to 2.5 and used KM as unit category.

        :param number: Number to search unit category for
        :param category: Current unit category (some base category given from convertors)
        :param language: Language of the units
        :param original_unit: Unit used in original sentence
        :param translated_unit: Unit used in translated sentence
        :return: Final number with best available unit
        :rtype: Tuple[Number, Unit]
        """
        best_number, best_category = number, category

        if category == translated_unit.category:
            return number, translated_unit

        for category in units_categories_groups[category]:

            # there is no unit for given category
            if len(units.get_list_units_by_category_language()[language][category]) == 0:
                continue

            category_number = number / category.base_coefficient
            if best_number < 0 or (1 < category_number < best_number):
                best_number = category_number
                best_category = category

        best_unit = units.get_correct_unit(language, best_number, original_unit, strict_category=best_category)

        return best_number, best_unit

    @staticmethod
    def length_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert units of length between systems (SI and imperial)"""
        if UnitsSystem.SI == original_category.system and UnitsSystem.IMPERIAL in target_system:
            target_number = original_number / 0.3048
            target_category = UnitCategories.FT
        elif UnitsSystem.IMPERIAL == original_category.system and UnitsSystem.SI in target_system:
            target_number = original_number * 0.3048
            target_category = UnitCategories.M
        else:
            target_number = original_number
            target_category = original_category

        return target_number, target_category

    @staticmethod
    def weight_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert units of weight between systems (SI and imperial)"""
        if UnitsSystem.SI == original_category.system and UnitsSystem.IMPERIAL in target_system:
            target_number = original_number / 453.59237
            target_category = UnitCategories.LB
        elif UnitsSystem.IMPERIAL == original_category.system and UnitsSystem.SI in target_system:
            target_number = original_number * 453.59237
            target_category = UnitCategories.G
        else:
            target_number = original_number
            target_category = original_category

        return target_number, target_category

    @staticmethod
    def area_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert units of area between systems (SI and imperial)"""
        if UnitsSystem.SI == original_category.system and UnitsSystem.IMPERIAL in target_system:
            target_number = original_number * 10.764
            target_category = UnitCategories.FT2
        elif UnitsSystem.IMPERIAL == original_category.system and UnitsSystem.SI in target_system:
            target_number = original_number / 10.764
            target_category = UnitCategories.M2
        else:
            target_number = original_number
            target_category = original_category

        return target_number, target_category

    @staticmethod
    def volume_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert units of volume between systems (SI and imperial)"""
        if UnitsSystem.SI == original_category.system and UnitsSystem.IMPERIAL in target_system:
            target_number = original_number * 35.315
            target_category = UnitCategories.FT3
        elif UnitsSystem.IMPERIAL == original_category.system and UnitsSystem.SI in target_system:
            target_number = original_number / 35.315
            target_category = UnitCategories.M3
        else:
            target_number = original_number
            target_category = original_category

        return target_number, target_category

    @staticmethod
    def currency_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert currencies"""

        categories_strings = {
            UnitCategories.CZK: 'CZK',
            UnitCategories.USD: 'USD',
            UnitCategories.GBP: 'GBP',
            UnitCategories.EUR: 'EUR',
        }

        currencies_system_categories = {
            UnitsSystem.CZK: UnitCategories.CZK,
            UnitsSystem.USD: UnitCategories.USD,
            UnitsSystem.GBP: UnitCategories.GBP,
            UnitsSystem.EUR: UnitCategories.EUR,
        }

        target_category = None

        for system, category in currencies_system_categories.items():
            if system in target_system:
                target_category = category
                break

        if not target_category:
            return original_number, original_category

        rate = exchange_rates_convertor.get_rate(categories_strings[original_category], categories_strings[target_category], original_number)
        return rate, target_category

    @staticmethod
    def temperature_convertor(original_number: Number, original_category: UnitCategory, target_system: List[UnitsSystem]) -> Tuple[Number, UnitCategory]:
        """Convert temperatures (between Celsius and Fahrenheit)"""
        if UnitsSystem.C == original_category.system and UnitsSystem.F in target_system:
            target_number = original_number * 1.8 + 32
            target_category = UnitCategories.F
        elif UnitsSystem.F == original_category.system and UnitsSystem.C in target_system:
            target_number = (original_number - 32) / 1.8
            target_category = UnitCategories.C
        else:
            target_number = original_number
            target_category = original_category

        return target_number, target_category


class UnitCategories:
    """List of all unit categories (units) with basic information"""
    MS = UnitCategory(UnitsSystem.SI, None, None)
    KMH = UnitCategory(UnitsSystem.SI, MS, 1000 / 3600)
    M2 = UnitCategory(UnitsSystem.SI, None, None, conversion=UnitsConvertors.area_convertor)
    KM2 = UnitCategory(UnitsSystem.SI, M2, 1000000)
    M3 = UnitCategory(UnitsSystem.SI, None, None, conversion=UnitsConvertors.volume_convertor)
    M = UnitCategory(UnitsSystem.SI, None, None, conversion=UnitsConvertors.length_convertor)
    KM = UnitCategory(UnitsSystem.SI, M, 1000)
    DM = UnitCategory(UnitsSystem.SI, M, 0.1)
    CM = UnitCategory(UnitsSystem.SI, M, 0.01)
    MM = UnitCategory(UnitsSystem.SI, M, 0.001)
    G = UnitCategory(UnitsSystem.SI, None, None, conversion=UnitsConvertors.weight_convertor)
    KG = UnitCategory(UnitsSystem.SI, G, 1000)
    LB = UnitCategory(UnitsSystem.IMPERIAL, None, None, conversion=UnitsConvertors.weight_convertor)
    FT = UnitCategory(UnitsSystem.IMPERIAL, None, None, conversion=UnitsConvertors.length_convertor)
    IN = UnitCategory(UnitsSystem.IMPERIAL, FT, 1 / 12)
    YD = UnitCategory(UnitsSystem.IMPERIAL, FT, 3)
    MI = UnitCategory(UnitsSystem.IMPERIAL, FT, 5280)
    FT2 = UnitCategory(UnitsSystem.IMPERIAL, None, None, conversion=UnitsConvertors.area_convertor)
    FT3 = UnitCategory(UnitsSystem.IMPERIAL, None, None, conversion=UnitsConvertors.volume_convertor)
    MI2 = UnitCategory(UnitsSystem.IMPERIAL, FT2, 27878400)
    CZK = UnitCategory(UnitsSystem.CZK, None, None, conversion=UnitsConvertors.currency_convertor)
    USD = UnitCategory(UnitsSystem.USD, None, None, conversion=UnitsConvertors.currency_convertor)
    GBP = UnitCategory(UnitsSystem.GBP, None, None, conversion=UnitsConvertors.currency_convertor)
    EUR = UnitCategory(UnitsSystem.EUR, None, None, conversion=UnitsConvertors.currency_convertor)
    C = UnitCategory(UnitsSystem.C, None, None, conversion=UnitsConvertors.temperature_convertor)
    F = UnitCategory(UnitsSystem.F, None, None, conversion=UnitsConvertors.temperature_convertor)

    @staticmethod
    def get_categories_by_groups() -> Dict[UnitCategory, List[UnitCategory]]:
        """List of all unit categories divided into lists by base categories"""
        categories_groups = {}

        all_categories = [a for a in dir(UnitCategories) if not a.startswith('__')]
        for category in all_categories:
            category_object = getattr(UnitCategories, category)
            if callable(category_object):
                continue

            if category_object.base is None and category_object not in categories_groups.keys():
                categories_groups[category_object] = []
            else:
                if category_object.base not in categories_groups.keys():
                    categories_groups[category_object.base] = []

                categories_groups[category_object.base].append(category_object)

        return categories_groups


units_categories_groups = UnitCategories.get_categories_by_groups()


class Unit:
    """Class for holding information about one unit form (eg. 'meter' and 'meters' are different Unit Instances)

    :ivar word: Text form of the unit
    :ivar category: Category of the unit
    :ivar language: Language of the unit
    :ivar numbers_validity: Numbers for whose is this unit form valid (singular forms, etc.)
    :ivar abbreviation: Flag whenever the unit form is an abbreviation
    :ivar dialect: Dialect of the unit form (british or american english)
    :ivar before_number: Flag whenever the unit can be placed in front of the number
    :param word: Text form of the unit
    :param category: Category of the unit
    :param language: Language of the unit
    :param numbers_validity: Numbers for whose is this unit form valid (singular forms, etc.)
    :param abbreviation: Flag whenever the unit form is an abbreviation
    :param dialect: Dialect of the unit form (british or american english)
    :param before_number: Flag whenever the unit can be placed in front of the number
    """

    def __init__(self,
                 word: str,
                 category: UnitCategory,
                 language: Language,
                 numbers_validity: Optional[List[Union[int, tuple, object]]],
                 abbreviation: bool,
                 dialect: Optional[UnitDialect],
                 before_number: bool = False):
        self.word = word
        self.category = category
        self.language = language
        self.numbers_validity = numbers_validity
        self.abbreviation = abbreviation
        self.before_number = before_number
        self.dialect = dialect

    @staticmethod
    def number_pass_numbers_validity(validity: List, number: Number) -> bool:
        """Checks whenever the unit validity rules matches the number"""
        if isinstance(number, float):
            return True if float in validity else False

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
    """Wrapper for list of all units and related methods."""

    def __init__(self):
        self.__units = []
        self.__units_by_languages = {}
        self.__units_before_by_languages = {}
        self.__units_by_language_category = {}
        self.__single_symbol = []
        self.__regex_unit_for_language = {}
        self.__regex_unit_before_for_language = {}

    def add_unit(self, unit: Unit):
        """Add new unit to the list and remove cached values"""
        self.__units.append(unit)
        self.__units_by_languages = {}
        self.__units_before_by_languages = {}
        self.__regex_unit_for_language = {}
        self.__regex_unit_before_for_language = {}
        self.__units_by_language_category = None
        self.__single_symbol = []

    def get_correct_unit(self, language: Language, number: Union[float, int], original_unit: Unit, *, strict_category=None, modifier=False, abbreviation=None) -> Unit:
        """Find best unit form to use for given number.

        All units are marked with score for different criteria (whenever it
        is number modifier, abbreviation and maily if it passed the validity check).

        :param language: Language of the unit
        :param number: Number to find unit for
        :param original_unit: Unit used in source sentence
        :param strict_category: Category of the searched unit
        :param modifier: Whenever looking for unit to number modifier
        :param abbreviation: Whenever looking for abbreviation unit
        :return: Unit with best match
        """
        strict_category = original_unit.category if not strict_category else strict_category

        options_list = []
        for unit in self.__units:
            if unit.language != language or unit.category != strict_category:
                continue

            score = 0

            if modifier and '-' in unit.word:
                score += 1

            if abbreviation is None and unit.abbreviation == original_unit.abbreviation:
                score += 2

            elif abbreviation is False and not unit.abbreviation:
                score += 2

            elif abbreviation is True and unit.abbreviation:
                score += 2

            if not unit.numbers_validity:
                score += 1

            elif Unit.number_pass_numbers_validity(unit.numbers_validity, number):
                score += 3

            options_list.append((score, unit))

        options_list.sort(key=lambda tup: tup[0], reverse=True)
        return options_list[0][1]

    def convert_number(self, target_language: Language, target_unit_system: List[UnitsSystem], actual_number: Number, original_unit: Unit, translated_unit: Unit) -> Tuple[Optional[Number], Optional[Unit]]:
        """Convert number with unit into different unit system

        Based on target unit system some unit category is selected, number converted and best fitting
        unit is selected.

        :param target_language: Language of the sentence and desired unit
        :param target_unit_system: List of UnitSystems preferred by user
        :param actual_number: Number from translated sentence to be converted
        :param original_unit: Unit of the actual number
        :param translated_unit: Unit used in the translated sentence
        :return: Best fitting number and unit
        """
        actual_category = original_unit.category
        if actual_category.base:
            actual_number = actual_number * original_unit.category.base_coefficient
            actual_category = original_unit.category.base

        if not actual_category.conversion:
            return None, None

        converted_number, converted_category = actual_category.conversion(actual_number, actual_category, target_unit_system)
        converted_number, converted_unit = UnitsConvertors.get_best_unit_for_converted_number(converted_number, converted_category, target_language, original_unit, translated_unit)

        return converted_number, converted_unit

    def convert_to_base_in_category(self, unit: Unit, number: Number) -> Number:
        """Convert number to base unit in the category (eg. 1 km is converted to 1000 meters)"""
        if not unit.category.base:
            return number

        return number * unit.category.base_coefficient

    def convert_to_base_in_another_system(self, unit: Unit, number: Number, needed_category: UnitCategory) -> Optional[Number]:
        """Convert number to base unit in the category and convert that to another unit system"""
        actual_category = unit.category
        if actual_category.base:
            number = number * unit.category.base_coefficient
            actual_category = unit.category.base

        converted_number, converted_category = actual_category.conversion(number, actual_category, [needed_category.system])

        if converted_category != needed_category:
            return None

        return converted_number

    def get_list_units_by_category_language(self) -> Dict[Language, Dict[UnitCategory, List[Unit]]]:
        """Get list of units divided by language and unit category. Uses caching"""
        if self.__units_by_language_category:
            return self.__units_by_language_category

        self.__units_by_language_category = {lang: {} for lang in Languages.get_languages_list()}

        for unit in self.__units:
            if unit.category not in self.__units_by_language_category[unit.language]:
                self.__units_by_language_category[unit.language][unit.category] = []

            self.__units_by_language_category[unit.language][unit.category].append(unit)

        return self.__units_by_language_category

    def get_units_by_category_language(self, category: UnitCategory, language: Language) -> List[Unit]:
        """Get list of units by given language and unit category"""
        if not self.__units_by_language_category:
            self.get_list_units_by_category_language()

        return self.__units_by_language_category[language][category]

    def get_unit_by_word(self, word: str, language: Language) -> Optional[Unit]:
        """Get first unit with given word in given language"""
        return next((unit for unit in self.get_all_units_for_language(language) if unit.word == word), None)

    def get_units_words_list(self, language: Language) -> List[str]:
        """Get first unit with given word in given language"""
        return [unit.word for unit in self.get_all_units_for_language(language)]

    def get_regex_units_for_language(self, language: Language) -> str:
        """Get list of words of units in given language separated by |"""
        if language not in self.__regex_unit_for_language:
            self.__regex_unit_for_language[language] = '|'.join([re.escape(unit.word) for unit in self.get_all_units_for_language(language)])

        return self.__regex_unit_for_language[language]

    def get_regex_units_for_language_before_numbers(self, language: Language) -> str:
        """Get list of words of units used before number in given language separated by |"""
        if language not in self.__regex_unit_before_for_language:
            self.__regex_unit_before_for_language[language] = '|'.join([re.escape(unit.word) for unit in self.get_all_units_for_language(language) if unit.before_number])

        return self.__regex_unit_before_for_language[language]

    def get_units_for_language_before_numbers_list(self, language: Language) -> List[str]:
        """Get list of words of units used before number in given language"""
        if language not in self.__units_before_by_languages:
            self.__units_before_by_languages[language] = [unit.word for unit in self.get_all_units_for_language(language) if unit.before_number]

        return self.__units_before_by_languages[language]

    def get_all_units_for_language(self, language: Language) -> List[Unit]:
        """Get list of units by language"""
        if language not in self.__units_by_languages:
            self.__units_by_languages[language] = []
            for unit in self.__units:
                if unit.language == language:
                    self.__units_by_languages[language].append(unit)

        return self.__units_by_languages[language]


numbers_validity_ones = [-1, 1]
numbers_validity_not_ones = [(None, -1), (1, None), float]
numbers_validity_2_3_4 = [-4, -3, -2, 2, 3, 4]
numbers_validity_more_than_5 = [(None, -4), (4, None)]
numbers_validity_decimal = [float]

units = UnitsWrapper()

units.add_unit(Unit('km/h', UnitCategories.KMH, Languages.CS, None, True, None))
units.add_unit(Unit('km / h', UnitCategories.KMH, Languages.CS, None, True, None))
units.add_unit(Unit('kph', UnitCategories.KMH, Languages.CS, None, True, None))
units.add_unit(Unit('kilometr za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometry za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('kilometrů za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('kilometru za hodinu', UnitCategories.KMH, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('kilometru v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('kilometrů v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('kilometr v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometry v hodině', UnitCategories.KMH, Languages.CS, numbers_validity_2_3_4, False, None))

units.add_unit(Unit('km/h', UnitCategories.KMH, Languages.EN, None, True, None))
units.add_unit(Unit('km / h', UnitCategories.KMH, Languages.EN, None, True, None))
units.add_unit(Unit('kph', UnitCategories.KMH, Languages.EN, None, True, None))
units.add_unit(Unit('kilometers per hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometer per hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometre per hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometres per hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('kilometres an hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('kilometers an hour', UnitCategories.KMH, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometer an hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometre an hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometer-an-hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometre-an-hour', UnitCategories.KMH, Languages.EN, numbers_validity_ones, False, None))

units.add_unit(Unit('m/s', UnitCategories.MS, Languages.CS, None, True, None))
units.add_unit(Unit('m / s', UnitCategories.MS, Languages.CS, None, True, None))
units.add_unit(Unit('mps', UnitCategories.MS, Languages.CS, None, True, None))
units.add_unit(Unit('metr za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('metry za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('metrů za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('metru za sekundu', UnitCategories.MS, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('m/s', UnitCategories.MS, Languages.EN, None, True, None))
units.add_unit(Unit('m / s', UnitCategories.MS, Languages.EN, None, True, None))
units.add_unit(Unit('mps', UnitCategories.MS, Languages.EN, None, True, None))
units.add_unit(Unit('meters per second', UnitCategories.MS, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('meter per second', UnitCategories.MS, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('metres per second', UnitCategories.MS, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('metre per second', UnitCategories.MS, Languages.EN, numbers_validity_ones, False, None))

units.add_unit(Unit('m2', UnitCategories.M2, Languages.CS, None, True, None))
units.add_unit(Unit('metr čtvereční', UnitCategories.M2, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('metru čtverečního', UnitCategories.M2, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('metry čtvereční', UnitCategories.M2, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('metrů čtverečních', UnitCategories.M2, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('m2', UnitCategories.M2, Languages.EN, None, True, None))
units.add_unit(Unit('square meter', UnitCategories.M2, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('square meters', UnitCategories.M2, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('square metre', UnitCategories.M2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square metres', UnitCategories.M2, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('square-metre', UnitCategories.M2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square-meter', UnitCategories.M2, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))

units.add_unit(Unit('km2', UnitCategories.KM2, Languages.CS, None, True, None))
units.add_unit(Unit('kilometr čtvereční', UnitCategories.KM2, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometru čtverečního', UnitCategories.KM2, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('kilometry čtvereční', UnitCategories.KM2, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('kilometrů čtverečních', UnitCategories.KM2, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('km2', UnitCategories.KM2, Languages.EN, None, True, None))
units.add_unit(Unit('square kilometer', UnitCategories.KM2, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('square kilometers', UnitCategories.KM2, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('square kilometre', UnitCategories.KM2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square kilometres', UnitCategories.KM2, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('square-kilometre', UnitCategories.KM2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square-kilometer', UnitCategories.KM2, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))

units.add_unit(Unit('m3', UnitCategories.M3, Languages.CS, None, True, None))
units.add_unit(Unit('metr krychlový', UnitCategories.M3, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('metru krychlového', UnitCategories.M3, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('metry krychlové', UnitCategories.M3, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('metrů krychlových', UnitCategories.M3, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('m3', UnitCategories.M3, Languages.EN, None, True, None))
units.add_unit(Unit('cubic meter', UnitCategories.M3, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('cubic meters', UnitCategories.M3, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('cubic metre', UnitCategories.M3, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('cubic metres', UnitCategories.M3, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('km', UnitCategories.KM, Languages.CS, None, True, None))
units.add_unit(Unit('kilometr', UnitCategories.KM, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometry', UnitCategories.KM, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('kilometrů', UnitCategories.KM, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('kilometru', UnitCategories.KM, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('km', UnitCategories.KM, Languages.EN, None, True, None))
units.add_unit(Unit('kilometers', UnitCategories.KM, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometer', UnitCategories.KM, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('kilometre', UnitCategories.KM, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('kilometres', UnitCategories.KM, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('m', UnitCategories.M, Languages.CS, None, True, None))
units.add_unit(Unit('metr', UnitCategories.M, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('metry', UnitCategories.M, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('metrů', UnitCategories.M, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('metru', UnitCategories.M, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('m', UnitCategories.M, Languages.EN, None, True, None))
units.add_unit(Unit('meters', UnitCategories.M, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('meter', UnitCategories.M, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('metre', UnitCategories.M, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('metres', UnitCategories.M, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('dm', UnitCategories.DM, Languages.CS, None, True, None))
units.add_unit(Unit('decimetr', UnitCategories.DM, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('decimetry', UnitCategories.DM, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('decimetrů', UnitCategories.DM, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('decimetru', UnitCategories.DM, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('dm', UnitCategories.DM, Languages.EN, None, True, None))
units.add_unit(Unit('decimeters', UnitCategories.DM, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('decimeter', UnitCategories.DM, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('decimetre', UnitCategories.DM, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('decimetres', UnitCategories.DM, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('cm', UnitCategories.CM, Languages.CS, None, True, None))
units.add_unit(Unit('centimetr', UnitCategories.CM, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('centimetry', UnitCategories.CM, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('centimetrů', UnitCategories.CM, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('centimetru', UnitCategories.CM, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('cm', UnitCategories.CM, Languages.EN, None, True, None))
units.add_unit(Unit('centimeters', UnitCategories.CM, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('centimeter', UnitCategories.CM, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('centimetre', UnitCategories.CM, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('centimetres', UnitCategories.CM, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('mm', UnitCategories.MM, Languages.CS, None, True, None))
units.add_unit(Unit('milimetr', UnitCategories.MM, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('milimetry', UnitCategories.MM, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('milimetrů', UnitCategories.MM, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('milimetru', UnitCategories.MM, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('mm', UnitCategories.MM, Languages.EN, None, True, None))
units.add_unit(Unit('millimeters', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, False, UnitDialect.AmE))
units.add_unit(Unit('millimeter', UnitCategories.MM, Languages.EN, numbers_validity_ones, False, UnitDialect.AmE))
units.add_unit(Unit('milimetre', UnitCategories.MM, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('millimetre', UnitCategories.MM, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('milimetres', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('millimetres', UnitCategories.MM, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('kg', UnitCategories.KG, Languages.CS, None, True, None))
units.add_unit(Unit('kilogram', UnitCategories.KG, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('kilogramy', UnitCategories.KG, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('kilogramů', UnitCategories.KG, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('kilogramu', UnitCategories.KG, Languages.CS, numbers_validity_decimal, False, None))
units.add_unit(Unit('kila', UnitCategories.KG, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('kilo', UnitCategories.KG, Languages.CS, [(None, -4), -1, 1, (4, None)], False, None))
units.add_unit(Unit('kil', UnitCategories.KG, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('kg', UnitCategories.KG, Languages.EN, None, True, None))
units.add_unit(Unit('kilograms', UnitCategories.KG, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('kilogram', UnitCategories.KG, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('kilos', UnitCategories.KG, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('g', UnitCategories.G, Languages.CS, None, True, None))
units.add_unit(Unit('gram', UnitCategories.G, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('gramy', UnitCategories.G, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('gramů', UnitCategories.G, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('gramu', UnitCategories.G, Languages.CS, numbers_validity_decimal, False, None))

units.add_unit(Unit('g', UnitCategories.G, Languages.EN, None, True, None))
units.add_unit(Unit('grams', UnitCategories.G, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('gram', UnitCategories.G, Languages.EN, numbers_validity_ones, False, None))

units.add_unit(Unit('°C', UnitCategories.C, Languages.CS, None, True, None))
units.add_unit(Unit('° C', UnitCategories.C, Languages.CS, None, True, None))
units.add_unit(Unit('stupeň celsia', UnitCategories.C, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stupeň Celsia', UnitCategories.C, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stupně celsia', UnitCategories.C, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stupně Celsia', UnitCategories.C, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stupňů celsia', UnitCategories.C, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('stupňů Celsia', UnitCategories.C, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('°C', UnitCategories.C, Languages.EN, None, True, None))
units.add_unit(Unit('° C', UnitCategories.C, Languages.EN, None, True, None))
units.add_unit(Unit('degree Celsius', UnitCategories.C, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('degree celsius', UnitCategories.C, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('degrees Celsius', UnitCategories.C, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('degrees celsius', UnitCategories.C, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('°F', UnitCategories.F, Languages.CS, None, True, None))
units.add_unit(Unit('° F', UnitCategories.F, Languages.CS, None, True, None))
units.add_unit(Unit('stupeň fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stupeň Fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stupně fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stupně Fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stupňů fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('stupňů Fahrenheita', UnitCategories.F, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('°F', UnitCategories.F, Languages.EN, None, True, None))
units.add_unit(Unit('° F', UnitCategories.F, Languages.EN, None, True, None))
units.add_unit(Unit('degree Fahrenheit', UnitCategories.F, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('degree fahrenheit', UnitCategories.F, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('degrees Fahrenheit', UnitCategories.F, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('degrees fahrenheit', UnitCategories.F, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('palec', UnitCategories.IN, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('palce', UnitCategories.IN, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('palců', UnitCategories.IN, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('inch', UnitCategories.IN, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('inches', UnitCategories.IN, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('stopa čtvereční', UnitCategories.FT2, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stopy čtvereční', UnitCategories.FT2, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stop čtverečních', UnitCategories.FT2, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('square foot', UnitCategories.FT2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square-foot', UnitCategories.FT2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square feet', UnitCategories.FT2, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('square-feet', UnitCategories.FT2, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('stopa krychlová', UnitCategories.FT3, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stopy krychlové', UnitCategories.FT3, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stop krychlových', UnitCategories.FT3, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('cubic foot', UnitCategories.FT3, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('cubic-foot', UnitCategories.FT3, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('cubic feet', UnitCategories.FT3, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('cubic-feet', UnitCategories.FT3, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('stopa', UnitCategories.FT, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('stopy', UnitCategories.FT, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('stop', UnitCategories.FT, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('ft', UnitCategories.FT, Languages.EN, None, True, None))
units.add_unit(Unit('foot', UnitCategories.FT, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('feet', UnitCategories.FT, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('yard', UnitCategories.YD, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('yardy', UnitCategories.YD, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('yardů', UnitCategories.YD, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('yd', UnitCategories.YD, Languages.EN, None, True, None))
units.add_unit(Unit('yard', UnitCategories.YD, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('yards', UnitCategories.YD, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('čtvereční míle', UnitCategories.MI2, Languages.CS, numbers_validity_ones + numbers_validity_2_3_4, False, None))
units.add_unit(Unit('čtverečních mil', UnitCategories.MI2, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('square mile', UnitCategories.MI2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square-mile', UnitCategories.MI2, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('square miles', UnitCategories.MI2, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('square-miles', UnitCategories.MI2, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('míle', UnitCategories.MI, Languages.CS, numbers_validity_ones + numbers_validity_2_3_4, False, None))
units.add_unit(Unit('mil', UnitCategories.MI, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('mi', UnitCategories.MI, Languages.EN, None, True, None))
units.add_unit(Unit('mile', UnitCategories.MI, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('miles', UnitCategories.MI, Languages.EN, numbers_validity_not_ones, False, None))

# units.add_unit(Unit('pounds', UnitCategories.LB, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('kč', UnitCategories.CZK, Languages.CS, None, True, None))
units.add_unit(Unit(',-kč', UnitCategories.CZK, Languages.CS, None, True, None))
units.add_unit(Unit('Kč', UnitCategories.CZK, Languages.CS, None, True, None))
units.add_unit(Unit(',-Kč', UnitCategories.CZK, Languages.CS, None, True, None))
units.add_unit(Unit('korun českých', UnitCategories.CZK, Languages.CS, numbers_validity_more_than_5, False, None))
units.add_unit(Unit('koruna česká', UnitCategories.CZK, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('koruny české', UnitCategories.CZK, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('koruny', UnitCategories.CZK, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('korun', UnitCategories.CZK, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('CZK', UnitCategories.CZK, Languages.EN, None, True, None, True))
units.add_unit(Unit('crowns', UnitCategories.CZK, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('Czech crowns', UnitCategories.CZK, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('kroner', UnitCategories.CZK, Languages.EN, [], False, None))
units.add_unit(Unit('kroners', UnitCategories.CZK, Languages.EN, [], False, None))

units.add_unit(Unit('$', UnitCategories.USD, Languages.CS, None, True, None, True))
units.add_unit(Unit('USD', UnitCategories.USD, Languages.CS, None, True, None, True))
units.add_unit(Unit('dolar', UnitCategories.USD, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('dolary', UnitCategories.USD, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('dolarů', UnitCategories.USD, Languages.CS, numbers_validity_2_3_4, False, None))

units.add_unit(Unit('$', UnitCategories.USD, Languages.EN, None, True, None, True))
units.add_unit(Unit('USD', UnitCategories.USD, Languages.EN, None, True, None, True))
units.add_unit(Unit('dollar', UnitCategories.USD, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('dollars', UnitCategories.USD, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('€', UnitCategories.EUR, Languages.CS, None, True, None, True))
units.add_unit(Unit('EUR', UnitCategories.EUR, Languages.CS, None, True, None, True))
units.add_unit(Unit('euro', UnitCategories.EUR, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('eura', UnitCategories.EUR, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('eur', UnitCategories.EUR, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('€', UnitCategories.EUR, Languages.EN, None, True, None, True))
units.add_unit(Unit('EUR', UnitCategories.EUR, Languages.EN, None, True, None, True))
units.add_unit(Unit('euro', UnitCategories.EUR, Languages.EN, numbers_validity_ones, False, None))
units.add_unit(Unit('euros', UnitCategories.EUR, Languages.EN, numbers_validity_not_ones, False, None))

units.add_unit(Unit('£', UnitCategories.GBP, Languages.CS, None, True, None, True))
units.add_unit(Unit('GBP', UnitCategories.GBP, Languages.CS, None, True, None, True))
units.add_unit(Unit('libra', UnitCategories.GBP, Languages.CS, numbers_validity_ones, False, None))
units.add_unit(Unit('libry', UnitCategories.GBP, Languages.CS, numbers_validity_2_3_4, False, None))
units.add_unit(Unit('liber', UnitCategories.GBP, Languages.CS, numbers_validity_more_than_5, False, None))

units.add_unit(Unit('£', UnitCategories.GBP, Languages.EN, None, True, None, True))
units.add_unit(Unit('GBP', UnitCategories.GBP, Languages.EN, None, True, None, True))
units.add_unit(Unit('pounds', UnitCategories.GBP, Languages.EN, numbers_validity_not_ones, False, None))
units.add_unit(Unit('pound', UnitCategories.GBP, Languages.EN, numbers_validity_ones, False, None))
