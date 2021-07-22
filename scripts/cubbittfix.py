#!/usr/bin/env python

import argparse
import sys

from fixer import Fixer, FixerConfigurator, FixerStatisticsMarks
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="Path to the configuration file")
parser.add_argument("--changes", default=False, action='store_true', help="Display only changed sentences")
parser.add_argument("--flags", default=False, action='store_true', help="Display ids of the statistics marks. Used only when flag changes is present.")


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
                print(";" + ";".join([str(mark.value) for mark in marks]) + ";" if args.flags else "",
                      source_sentence,
                      translated_sentence.strip(),
                      repaired_sentence.strip(), "",
                      sep='\n', end='\n\n')

        else:
            print(source_sentence, repaired_sentence, sep='\t')

    if args.flags:
        statistics_to_print = [(mark.value, mark.name, statistics[mark.value]) for mark in FixerStatisticsMarks]
        print(tabulate(statistics_to_print, headers=("ID", "Label", "#")), file=sys.stderr)
    else:
        statistics_to_print = [(mark.name, statistics[mark.value]) for mark in FixerStatisticsMarks]
        print(tabulate(statistics_to_print, headers=("Label", "#")), file=sys.stderr)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
