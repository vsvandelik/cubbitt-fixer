from typing import List, Dict


class WrongLanguage(ValueError):
    """Exception when unsupported language is used."""
    pass


class Language:
    """Class representing language of the sentence.

    It holds basic information about language as acronym,
    separators, etc. (more detailed in the list of parameters).

    :param acronym: string acronym of language
    :param approximately_phrases: words used in given language for approximately figures
    :param decimal_separator: char used to separate decimal part of non-integer number
    :param thousands_separator: char used to separate thousands in long numbers
    """

    def __init__(self,
                 acronym: str,
                 approximately_phrases: List[str],
                 decimal_separator: str,
                 thousands_separator: str,
                 big_numbers_scale: Dict[str, int]):
        self.acronym = acronym
        self.approximately_phrases = approximately_phrases
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator
        self.big_numbers_scale = big_numbers_scale

        self.big_numbers_scale_keys = "|".join(self.big_numbers_scale.keys())


class Languages:
    """Wrapper of languages supported by the package."""

    #: Instance of the czech language
    CS = Language('cs', ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'], ',', '.', {
        'tisíce': 1000,
        'tisíc': 1000,
        'miliony': 1000000,
        'milionů': 1000000,
        'milion': 1000000,
        'miliarda': 1000000000,
        'miliardy': 1000000000,
        'miliard': 1000000000,
        'biliony': 1000000000000,
        'bilionů': 1000000000000,
        'bilion': 1000000000000,
        'biliarda': 1000000000000000,
        'biliardy': 1000000000000000,
        'biliard': 1000000000000000,
        'triliony': 100000000000000000,
        'trilionů': 1000000000000000000,
        'trilion': 1000000000000000000,
        'triliarda': 1000000000000000000000,
        'triliardy': 1000000000000000000000,
        'triliard': 1000000000000000000000
    })

    #: Instance of the english language
    EN = Language('en', ['about', 'around', 'roughly', 'approximately'], '.', ',', {
        'thousand': 1000,
        'thousands': 1000,
        'million': 1000000,
        'millions': 1000000,
        'billion': 1000000000,
        'billions': 1000000000,
        'trillion': 1000000000000,
        'trillions': 1000000000000,
        'quadrillion': 1000000000000000,
        'quadrillions': 1000000000000000,
        'quintillion': 1000000000000000000,
        'quintillions': 1000000000000000000,
        'sextillion': 1000000000000000000000,
        'sextillions': 1000000000000000000000,
    })

    @staticmethod
    def get_language(acronym: str) -> Language:
        """It returns instance of language class based on acronym.

        :param acronym: str acronym of the language
        :raises WrongLanguage: exception thrown when given acronym is not valid
        """
        if acronym == Languages.CS.acronym:
            return Languages.CS
        elif acronym == Languages.EN.acronym:
            return Languages.EN
        else:
            raise WrongLanguage(f"Language with acronym {acronym} is not supported withing the package.")

    @staticmethod
    def get_languages_list() -> List[Language]:
        """Returns list of supported languages."""
        return [Languages.CS, Languages.EN]
