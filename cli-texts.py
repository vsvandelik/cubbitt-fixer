# coding=utf-8
import argparse
import os

from fixer import Fixer, FixerConfigurator
from fixer._statistics import StatisticsMarks
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Name of source file")
parser.add_argument("translation", help="Name of translation file")
parser.add_argument("config", help="Path to the configuration file")


def main(args):
    configuration = FixerConfigurator()
    configuration.load_from_file(args.config)

    fixer = Fixer(configuration)
    statistics = {mark.value: 0 for mark in StatisticsMarks}

    translation_file_parts = os.path.splitext(args.translation)
    output_file_name = translation_file_parts[0] + "-fixer" + translation_file_parts[1]

    with open(args.source, "r", encoding="utf8") as source_file, open(args.translation, "r", encoding="utf8") as translation_file, open(output_file_name, "w", encoding="utf8") as output_file :
        for source_line in source_file:  # checking the limit
            translated_line = translation_file.readline()

            repaired_sentence, marks = fixer.fix(source_line, translated_line)

            for mark in marks:
                statistics[mark.value] += 1

            if isinstance(repaired_sentence, str):
                output_file.write(repaired_sentence)
            else:
                output_file.write(translated_line)

    statistics_to_print = [(mark.name, statistics[mark.value]) for mark in StatisticsMarks]
    print(tabulate(statistics_to_print))


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
