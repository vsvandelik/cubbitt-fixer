from typing import List


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
                 thousands_separator: str):
        self.acronym = acronym
        self.approximately_phrases = approximately_phrases
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator


class Languages:
    """Wrapper of languages supported by the package."""

    #: Instance of the czech language
    CS = Language('cs', ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'], ',', '.')

    #: Instance of the english language
    EN = Language('en', ['about', 'around', 'roughly', 'approximately'], '.', ',')

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
