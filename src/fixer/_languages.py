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

    __SCALING_WORDS_VALIDITY = {
        'ones': [-1, 1],
        '2_3_4': [-4, -3, -2, 2, 3, 4],
        'more_than_5': [(None, -4), (4, None), float],
    }

    #: Instance of the czech language
    CS = Language('cs', ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'], ',', '.', {
        'sto': (100, __SCALING_WORDS_VALIDITY['ones']),
        'stě': (100, [-2, 2]),
        'sta': (100, [-4, -3, 3, 4]),
        'set': (100, __SCALING_WORDS_VALIDITY['more_than_5']),
        'tisíce': (1000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'tisíc': (1000, __SCALING_WORDS_VALIDITY['ones'] + __SCALING_WORDS_VALIDITY['more_than_5']),
        'miliony': (1000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'milióny': (1000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'milionů': (1000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'miliónů': (1000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'milionu': (1000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'miliónu': (1000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'milion': (1000000, __SCALING_WORDS_VALIDITY['ones']),
        'milión': (1000000, __SCALING_WORDS_VALIDITY['ones']),
        'miliarda': (1000000000, __SCALING_WORDS_VALIDITY['ones']),
        'miliardy': (1000000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'miliard': (1000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'biliony': (1000000000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'bilionů': (1000000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'bilionu': (1000000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'bilion': (1000000000000, __SCALING_WORDS_VALIDITY['ones']),
        'biliarda': (1000000000000000, __SCALING_WORDS_VALIDITY['ones']),
        'biliardy': (1000000000000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'biliard': (1000000000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'triliony': (100000000000000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'trilionů': (1000000000000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'trilionu': (1000000000000000000, __SCALING_WORDS_VALIDITY['more_than_5']),
        'trilion': (1000000000000000000, __SCALING_WORDS_VALIDITY['ones']),
        'triliarda': (1000000000000000000000, __SCALING_WORDS_VALIDITY['ones']),
        'triliardy': (1000000000000000000000, __SCALING_WORDS_VALIDITY['2_3_4']),
        'triliard': (1000000000000000000000, __SCALING_WORDS_VALIDITY['more_than_5'])
    })

    #: Instance of the english language
    EN = Language('en', ['about', 'around', 'roughly', 'approximately'], '.', ',', {
        'thousand': (1000, []),
        'thousands': (1000, None),
        'million': (1000000, []),
        'millions': (1000000, None),
        'billion': (1000000000, []),
        'billions': (1000000000, None),
        'bn': (1000000000, None),
        'trillion': (1000000000000, []),
        'trillions': (1000000000000, None),
        'quadrillion': (1000000000000000, []),
        'quadrillions': (1000000000000000, None),
        'quintillion': (1000000000000000000, []),
        'quintillions': (1000000000000000000, None),
        'sextillion': (1000000000000000000000, []),
        'sextillions': (1000000000000000000000, None),
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
