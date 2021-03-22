#!/usr/bin/python3.8

import re
import argparse

from fixer import _digits_translation as dt, _units

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Name of file to be checked")
parser.add_argument("source_lang", help="Label of source language of file (sentences on left)")
parser.add_argument("dest_lang", help="Label of translated language of file (sentences on right)")

parser.add_argument("--numbers", action="store_true", default=False, help="Filter numbers problems")
parser.add_argument("--interpunction", action="store_true", default=False, help="Filter interpunction problems")
parser.add_argument("--names", action="store_true", default=False, help="Filter names problems")

parser.add_argument("--limit", default=100000, type=int, help="Count of sentences to be checked")
parser.add_argument("--offset", default=0, help="Offset of sentences to be checked")


def generate_translated_variants(number: int, rest: str, left_lang: str, recalculated_number: float, recalculated_rest: str) -> list:
    """
    Generates all possible variants (cartesian product) of number with unit.

    Actual supported patterns are:
      - 25cm
      - 25 cm
      - 25-cm

    :param number: numeric value
    :param rest: units of numeric value
    :param left_lang: language of left sentence
    :return: list with all possible variants
    """
    patterns = ["{}{}", "{} {}", "{}-{}"]

    numbers = [number, '{:,}'.format(number)]
    if left_lang == 'cs' and number in dt.en.keys():  # rewrite digit as a string
        numbers.append(dt.en[number])
    elif left_lang == 'en' and number in dt.cs.keys():
        numbers.append(dt.cs[number])

    rests = [rest] + _units.units[rest]

    variants = []

    for pat in patterns:
        for num in numbers:
            for res in rests:
                variants.append(pat.format(num, res))

    return variants


number_patter = re.compile(rf"(\d+\s?(?:{_units.unitsString})\b)")
approx_phrases = {
    'cs': ['cca', 'zhruba', 'přibližně', 'asi', 'asi tak'],
    'en': ['about', 'around', 'roughly', 'approximately']
}


def numbers_filter(left: str, right: str, left_lang: str, right_lang: str) -> list:
    """
    Find non-valid translation of numbers with units. It searches in left given substring for some possible problematic
    substrings then it prepares all valid translations and finally it searches for that translations in right substring.
    If any valid translation is found, it reports a problem.

    :param left: text in original language
    :param right: translation
    :param left_lang: original language
    :param right_lang: translation language
    :return: list with problematic parts (not correctly translated)
    """
    parts = re.findall(number_patter, left)
    if len(parts) == 0:  # any number-digit part in left text
        return []

    problems = []

    for part in parts:

        approximately = ""
        if re.search(f"({'|'.join(approx_phrases[left_lang])}) {part}"   , left):
            approximately = "cca "

        number = rest = None
        for idx in range(0, len(part)):
            if not part[idx].isdigit():
                number = int(part[:idx].strip())
                rest = part[idx:].strip(' -')
                break
        
        recalculated_number, recalculated_rest = _units.convert_unit(number, rest)
        variants = generate_translated_variants(number, rest, left_lang, recalculated_number, recalculated_rest)
        found = re.search("|".join(variants), right)
        if not found:
            problems.append("{}{} = {:.2f} {}".format(approximately, part, recalculated_number, recalculated_rest))

    return problems


name_pattern = re.compile(r"^.+([A-Z][a-z]+\b)")


def names_filter(left: str, right: str, left_lang: str, right_lang: str) -> list:
    """
    Experiment to filter translation problems with proper names. It searches for non-leading word with
    first capital letter and tries to find same word in translation. It it fails, the word is reported.

    It should not be used because the filter is not smart enough to search for real problems and it
    reports every translation of name.

    :param left: text in original language
    :param right: translation
    :param left_lang: original language
    :param right_lang: translation language
    :return: list with problematic parts (not correctly translated)
    """
    parts = re.findall(name_pattern, left)
    if len(parts) == 0:  # any proper name in original text
        return []

    problems = []

    for part in parts:
        found = re.search(part, right)
        if not found:
            problems.append(part)

    return problems


multiple_interpunction_pattern = re.compile(r"[.!?]\s[A-Z].*[.!?]")
question_mark_pattern = re.compile(r"\?\s.*[.!]\s*$")
question_mark_2_pattern = re.compile(r"\?\s*$")
exclamation_mark_pattern = re.compile(r"!\s.*[.?]\s*$")
exclamation_mark_2_pattern = re.compile(r"!\s*$")


def interpunction_filter(left: str, right: str, left_lang: str, right_lang: str) -> list:
    """
    Find problems with interpunction.

    Problem is reported when there is ? or ! inside of sentence, and in the translation is the mark
    at the end. It ignores sentences, where there is more that one of that mark.

    :param left: text in original language
    :param right: translation
    :param left_lang: original language
    :param right_lang: translation language
    :return: list of problematic parts
    """

    problems = []

    if re.search(question_mark_pattern, left):
        if re.search(question_mark_2_pattern, right):
            problems.append('?')

    if re.search(question_mark_pattern, right):
        if re.search(question_mark_2_pattern, left):
            problems.append('?')

    if re.search(exclamation_mark_pattern, left):
        if re.search(exclamation_mark_2_pattern, right):
            problems.append('!')

    if re.search(exclamation_mark_pattern, right):
        if re.search(exclamation_mark_2_pattern, left):
            problems.append('!')

    return problems


def filter_sentences(
        file: str,
        offset=0,
        limit=10000,
        left_lang='cs',
        right_lang='en',
        numbers=False,
        interpunction=False,
        names=False) -> list:
    """
    Process file line-by-line. Based on given parameters it can count in only part of input file.
    Each line is slitted into two parts (origin text and the translation) and sent to filters.

    If filters find some error, the sentence is reported to the user by printing it.

    :param file: name of input file
    :param offset: num of translated sentences to be ignored from start
    :param limit: num of translated sentences to be processed
    :param left_lang: language of sentences on left
    :param right_lang: language of sentences on right
    :param numbers: should be active numbers filter
    :param interpunction: should be active intepunction filter
    :param names: should be active names filter
    :return: list of tuples with possible problems
    """

    resuls = []

    with open(file, "r", encoding="utf8") as input_file:
        for _ in range(offset):  # skipping the offset
            next(input_file)

        last = None
        for line in input_file:  # checking the limit
            limit -= 1
            if limit == 0:
                break

            if line.isspace():
                continue

            left, right = line.split('\t')

            if left == last:  # skipping same sentences
                continue
            last = left

            problems = []
            if numbers:
                problems += numbers_filter(left, right, left_lang, right_lang)
            if interpunction:
                problems += interpunction_filter(left, right, left_lang, right_lang)
            if names:
                problems += names_filter(left, right, left_lang, right_lang)

            if len(problems):  # reporting errors
                resuls.append((problems, left, right))

    return resuls


if __name__ == "__main__":
    args = parser.parse_args()
    problems = filter_sentences(
        file=args.file, offset=args.offset, limit=args.limit,
        left_lang=args.source_lang, right_lang=args.dest_lang,
        numbers=args.numbers, interpunction=args.interpunction, names=args.names
    )

    for problem in problems:
        print(problem[0], problem[1], problem[2], sep='\n')
