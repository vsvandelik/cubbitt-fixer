import re

import digits_translation as dt
import units

number_patter = re.compile(rf"(\d+\s?(?:{units.unitsString})\b)")
name_pattern = re.compile(r"^.+([A-Z][a-z]+\b)")

def generate_translated_variants(number: int, rest: str) -> list:
    """
    Generates all possible variants (cartesian product) of number with unit.

    Actual supported patterns are:
      - 25cm
      - 25 cm
      - 25-cm

    :param number: numeric value
    :param rest: units of numeric value
    :return: list with all possible variants
    """
    patterns = ["{}{}", "{} {}", "{}-{}"]

    numbers = [number, '{:,}'.format(number)]
    if number in dt.en.keys():  # rewrite digit as a string
        numbers.append(dt.en[number])

    rests = [rest] + units.units[rest]

    variants = []

    for pat in patterns:
        for num in numbers:
            for res in rests:
                variants.append(pat.format(num, res))

    return variants


def numbers_filter(left: str, right: str) -> list:
    """
    Find non-valid translation of numbers with units. It searches in left given substring for some possible problematic
    substrings then it prepares all valid translations and finally it searches for that translations in right substring.
    If any valid translation is found, it reports a problem.

    :param left: text in original language
    :param right: translation
    :return: list with problematic parts (not correctly translated)
    """
    parts = re.findall(number_patter, left)
    if len(parts) == 0:  # any number-digit part in left text
        return []

    problems = []

    for part in parts:
        number = rest = None
        for idx in range(0, len(part)):
            if not part[idx].isdigit():
                number = int(part[:idx].strip())
                rest = part[idx:].strip()
                break

        variants = generate_translated_variants(number, rest)
        found = re.search("|".join(variants), right)
        if not found:
            problems.append(part)

    return problems


def names_filter(left: str, right: str) -> list:
    """
    Experiment to filter translation problems with proper names. It searches for non-leading word with
    first capital letter and tries to find same word in translation. It it fails, the word is reported.

    It should not be used because the filter is not smart enough to search for real problems and it
    reports every translation of name.

    :param left: text in original language
    :param right: translation
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


def filter_sentences(file: str, offset=0, limit=10000, ignore_limit=False) -> None:
    """
    Process file line-by-line. Based on given parameters it can count in only part of input file.
    Each line is slitted into two parts (origin text and the translation) and sent to filters.

    If filters find some error, the sentence is reported to the user by printing it.

    :param file: name of input file
    :param offset: num of rows to be ignored from start
    :param limit: num of rows to be processed
    :param ignore_limit: switch if the offset and limit should be ignored
    :return: None
    """
    with open(file, "r", encoding="utf8") as input_file:
        for _ in range(offset):  # skipping the offset
            next(input_file)

        last = None
        for line in input_file:
            if not ignore_limit:  # checking the limit
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
            problems += numbers_filter(left, right)
            # problems += names_filter(left, right)

            if len(problems):  # reporting errors
                print(problems, left, right, sep='\n')


if __name__ == "__main__":
    filter_sentences("sentences", limit=5000000)
    # filter_sentences("vzorek")
