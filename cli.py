# coding=utf-8
import argparse
import sys

from fixer import Fixer, FixerConfigurator, FixerStatisticsMarks
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="Path to the configuration file")
parser.add_argument("--changes", default=False, action='store_true', help="Display only changed sentences")


def main(args):
    configuration = FixerConfigurator()
    configuration.load_from_file(args.config)

    fixer = Fixer(configuration)
    statistics = {mark.value: 0 for mark in FixerStatisticsMarks}

    for line in sys.stdin:
        line = line.strip()

        if not line and not args.changes:
            print()
            continue

        source_sentence, translated_sentence = line.split('\t')
        repaired_sentence, has_changed, marks = fixer.fix(source_sentence, translated_sentence)

        for mark in marks:
            statistics[mark.value] += 1

        if args.changes:
            if has_changed:
                print(source_sentence, translated_sentence, repaired_sentence, sep='\n', end='\n\n')

        else:
            print(source_sentence, repaired_sentence, sep='\t')

    statistics_to_print = [(mark.name, statistics[mark.value]) for mark in FixerStatisticsMarks]
    print(tabulate(statistics_to_print))


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
