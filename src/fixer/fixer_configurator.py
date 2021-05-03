from enum import Enum, auto

import yaml

from ._aligner import get_aligners_list
from ._exchange_rates import get_exchange_rates_convertors_list, get_default_exchnage_rates_convertor
from ._languages import Languages
from ._lemmatization import get_lemmatizators_list
from ._name_recognition import get_names_tagger_list
from ._units import UnitsSystem


class FixerModes(Enum):
    FIXING = auto()
    RECALCULATING = auto()


class FixerTools(Enum):
    SEPARATORS = auto()
    NAMES = auto()
    UNITS = auto()


class FixerConfiguratorException(Exception):
    pass


class FixerConfigurator:

    def __init__(self):
        self.source_lang = None
        self.target_lang = None
        self.tools = []
        self.aligner = None
        self.lemmatizator = None
        self.names_tagger = None
        self.mode = None
        self.base_tolerance = None
        self.approximately_tolerance = None
        self.exchange_rates = None
        self.target_units = []

    def validate_configuration(self):
        if not self.source_lang or not self.target_lang:
            return False

        if FixerTools.NAMES in self.tools and not self.names_tagger:
            return False

        if FixerTools.UNITS in self.tools and not (self.aligner and self.lemmatizator and self.base_tolerance and self.approximately_tolerance):
            return False

        if FixerModes.RECALCULATING == self.mode and not (self.target_units and self.exchange_rates):
            return False

        return True

    def load_from_file(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)

            self.source_lang = self.get_language(config, 'source_lang')
            self.target_lang = self.get_language(config, 'source_lang')

            self.aligner = self.verify_and_get_instance(get_aligners_list(), config, 'aligner')
            self.lemmatizator = self.verify_and_get_instance(get_lemmatizators_list(), config, 'lemmatizator')
            self.names_tagger = self.verify_and_get_instance(get_names_tagger_list(), config, 'names_tagger')
            self.mode = self.verify_and_get_instance({'fixing': FixerModes.FIXING, 'recalculating': FixerModes.RECALCULATING}, config, 'mode')
            self.base_tolerance = self.verify_number_interval(0, 1, config, 'base_tolerance')
            self.approximately_tolerance = self.verify_number_interval(0, 1, config, 'approximately_tolerance')

            self.target_units = self.get_units_systems_by_names(config, 'target_units')
            self.exchange_rates = self.get_exchange_rates(config, 'exchange_rates')

            print(self.exchange_rates.get_rate('USD', 'CZK', 1))

    @staticmethod
    def verify_and_get_instance(instances: dict, config: dict, config_option: str):
        if config_option not in config.keys():
            FixerConfiguratorException(f"Configuration file is broken. Some required fields ({config_option}) are missing.")

        label = config[config_option]

        if label not in instances.keys():
            FixerConfiguratorException(f"{label} is not valid configuration option.")

        return instances[label]

    @staticmethod
    def verify_number_interval(min_value: float, max_value: float, config: dict, config_option: str):
        if config_option not in config.keys():
            FixerConfiguratorException(f"Configuration file is broken. Some required fields ({config_option}) are missing.")

        value = config[config_option]

        if not (min_value <= value <= max_value):
            FixerConfiguratorException(f"{value} is not valid configuration option. It should be between {min_value} and {max_value}")

        return value

    @staticmethod
    def get_units_systems_by_names(config: dict, config_option: str):
        if config_option not in config.keys():
            FixerConfiguratorException(f"Targets unit systems are not specified in the configuration file.")

        systems = {e.name: e.value for e in UnitsSystem}

        parsed_systems = []

        for target_unit in config[config_option]:
            if target_unit not in systems.keys():
                FixerConfiguratorException(f"Wrong definition of target unit system - {target_unit}.")
                return

            parsed_systems.append(systems[target_unit])

        return parsed_systems

    @staticmethod
    def get_language(config: dict, config_option: str):
        if config_option not in config.keys():
            FixerConfiguratorException(f"Language option is missing.")

        return Languages.get_language(config[config_option])

    @staticmethod
    def get_exchange_rates(config: dict, config_option: str):
        if config_option not in config.keys():
            FixerConfiguratorException(f"Exchange rates option is missing.")

        convertor = None

        if isinstance(config[config_option], str) and config[config_option] in get_exchange_rates_convertors_list().keys():
            convertor = get_exchange_rates_convertors_list()[config[config_option]]()
        elif isinstance(config[config_option], dict):
            default_convertor = get_default_exchnage_rates_convertor()
            convertor = get_exchange_rates_convertors_list()[default_convertor](config[config_option])

        return convertor
