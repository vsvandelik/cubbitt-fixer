from enum import Enum, auto

import yaml

from ._aligner import get_aligners_list
from ._exchange_rates import get_exchange_rates_convertors_list, get_default_exchange_rates_convertor, ExchangeRatesInterface
from ._languages import Languages, Language
from ._lemmatization import get_lemmatizators_list
from ._name_recognition import get_names_tagger_list
from ._units import UnitsSystem


class FixerModes(Enum):
    """List of modes to fixer can work in"""
    FIXING = auto()  #: Numbers with wrong unit or number are changed
    RECALCULATING = auto()  #: All numbers with units are changed


class FixerTools(Enum):
    """List of separate tools which can be run"""
    SEPARATORS = auto()  #: Fix the decimal and thousands separator
    NAMES = auto()  #: Fix the proper names of person
    UNITS = auto()  #: Fix numbers and units


class FixerConfiguratorException(Exception):
    """Exception indicating problem with configuration"""
    pass


class FixerConfigurator:
    """Class for loading and managing configuration of the package.

    :ivar source_lang: Language of the source sentences
    :ivar target_lang: Language of the target (translated) sentences
    :ivar aligner: Instance of the tool used for word-alignment
    :ivar lemmatizator: Instance of the tool used for sentence analysis
    :ivar names_tagger: Instance of the tool used for extracting names from sentence
    :ivar mode: Mode to be fixer working in (valid for units tool)
    :ivar base_tolerance: Number indicating approved number inaccuracy
    :ivar approximately_tolerance: Number indicating approved number inaccuracy for numbers marked as approximately
    :ivar exchange_rates: Instance of CNBExchangeRates holding the rates
    :ivar tools: list of tools to be used
    :ivar target_units: Units to be recalculated to when mode is recalculating
    """

    def __init__(self):
        self.source_lang = None
        self.target_lang = None
        self.aligner = None
        self.lemmatizator = None
        self.names_tagger = None
        self.mode = None
        self.base_tolerance = None
        self.approximately_tolerance = None
        self.exchange_rates = None
        self.tools = []
        self.target_units = []

    def load_from_file(self, filename: str):
        """Loads configuration from given file"""
        with open(filename, 'r', encoding='utf-8') as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)
            self.load_from_dict(config)

    def load_from_dict(self, config: dict):
        """Parse configuration from dictionary"""
        self.source_lang = self.__get_language(config, 'source_lang')
        self.target_lang = self.__get_language(config, 'target_lang')

        self.aligner = self.__verify_and_get_instance(get_aligners_list(), config, 'aligner')()
        self.lemmatizator = self.__verify_and_get_instance(get_lemmatizators_list(), config, 'lemmatizator')()
        self.names_tagger = self.__verify_and_get_instance(get_names_tagger_list(), config, 'names_tagger')()
        self.mode = self.__verify_and_get_instance({'fixing': FixerModes.FIXING, 'recalculating': FixerModes.RECALCULATING}, config, 'mode')
        self.base_tolerance = self.__verify_number_interval(0, 1, config, 'base_tolerance')
        self.approximately_tolerance = self.__verify_number_interval(0, 1, config, 'approximately_tolerance')

        self.target_units = self.__get_enum_items_by_names({e.name: e for e in UnitsSystem}, config, 'target_units')
        self.tools = self.__get_enum_items_by_names({e.name: e for e in FixerTools}, config, 'tools')
        self.exchange_rates = self.__get_exchange_rates(config, 'exchange_rates')

    @staticmethod
    def __verify_and_get_instance(instances: dict, config: dict, config_option: str):
        """Verify if value in dictionary is filled and valid"""
        if config_option not in config.keys():
            raise FixerConfiguratorException(f"Configuration file is broken. Some required fields ({config_option}) are missing.")

        label = config[config_option]

        if label not in instances.keys():
            raise FixerConfiguratorException(f"{label} is not valid configuration option.")

        return instances[label]

    @staticmethod
    def __verify_number_interval(min_value: float, max_value: float, config: dict, config_option: str):
        """Verify if value in dictionary is filled and valid (in a range)"""
        if config_option not in config.keys():
            raise FixerConfiguratorException(f"Configuration file is broken. Some required fields ({config_option}) are missing.")

        value = config[config_option]

        if not (min_value <= value <= max_value):
            raise FixerConfiguratorException(f"{value} is not valid configuration option. It should be between {min_value} and {max_value}")

        return value

    @staticmethod
    def __get_enum_items_by_names(values: dict, config: dict, config_option: str):
        """Verify if value in dictionary is filled and match it to the enum value"""

        if config_option not in config.keys():
            raise FixerConfiguratorException(f"{config_option} are not specified in the configuration file.")

        parsed_values = []

        for item in config[config_option]:
            item_uppercase = item.upper()
            if item_uppercase not in values.keys():
                raise FixerConfiguratorException(f"Wrong definition of {config_option} - {item}.")

            parsed_values.append(values[item_uppercase])

        return parsed_values

    @staticmethod
    def __get_language(config: dict, config_option: str) -> Language:
        """Verify if value in dictionary is filled and load language from the languages list"""

        if config_option not in config.keys():
            raise FixerConfiguratorException(f"Language option is missing.")

        return Languages.get_language(config[config_option])

    @staticmethod
    def __get_exchange_rates(config: dict, config_option: str) -> ExchangeRatesInterface:
        """Verify if value in dictionary is filled and load exchange rates"""

        if config_option not in config.keys():
            raise FixerConfiguratorException(f"Exchange rates option is missing.")

        convertor = None

        if isinstance(config[config_option], str) and config[config_option] in get_exchange_rates_convertors_list().keys():
            convertor = get_exchange_rates_convertors_list()[config[config_option]]
        elif isinstance(config[config_option], dict):
            default_convertor = get_default_exchange_rates_convertor()
            convertor = get_exchange_rates_convertors_list()[default_convertor].load_static_rates(config[config_option])

        return convertor

    def __validate_configuration(self) -> bool:
        """Check if there are all necessary items filled."""
        if not self.source_lang or not self.target_lang:
            return False

        if FixerTools.NAMES in self.tools and not self.names_tagger:
            return False

        if FixerTools.UNITS in self.tools and not (self.aligner and self.lemmatizator and self.base_tolerance and self.approximately_tolerance):
            return False

        if FixerModes.RECALCULATING == self.mode and not (self.target_units and self.exchange_rates):
            return False

        return True
