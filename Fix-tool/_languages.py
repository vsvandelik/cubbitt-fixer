from typing import List


class Language:

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
    CS = Language('cs', ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'], ',', '.')
    EN = Language('en', ['about', 'around', 'roughly', 'approximately'], '.', ',')

    @staticmethod
    def get_language(acronym: str):
        if acronym == Languages.CS.acronym:
            return Languages.CS
        elif acronym == Languages.EN.acronym:
            return Languages.EN
        else:
            raise Exception("wrong language")

    @staticmethod
    def get_languages_list():
        return Languages.CS, Languages.EN
