# coding=utf-8
import argparse

from fixer import Fixer, FixerConfigurator
from fixer._statistics import StatisticsMarks
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Name of file to be checked")
parser.add_argument("config", help="Path to the configuration file")
parser.add_argument("--limit", default=100000, type=int, help="Count of sentences to be checked")
parser.add_argument("--offset", default=0, type=int, help="Offset of sentences to be checked")
parser.add_argument("--texts", default=False, action='store_true')


def main(args):
    configuration = FixerConfigurator()
    configuration.load_from_file(args.config)

    fixer = Fixer(configuration)
    statistics = {mark.value: 0 for mark in StatisticsMarks}

    with open(args.file, "r", encoding="utf8") as input_file, open("output.txt", "w", encoding="utf8") as output_file:
        for _ in range(args.offset):  # skipping the offset
            next(input_file)

        last = None
        for line in input_file:  # checking the limit
            args.limit -= 1
            if args.limit == 0:
                break

            if line.isspace() and not args.texts:
                continue
            elif line.isspace():
                output_file.write("\n")
                continue

            left, right = line.split('\t')

            if left == last and not args.texts:  # skipping same sentences
                continue

            last = left

            left = left.strip()
            right = right.strip()

            repaired_sentence, marks = fixer.fix(left, right)

            for mark in marks:
                statistics[mark.value] += 1

            #if all([mark not in marks for mark in [StatisticsMarks.WRONG_NUMBER_CORRECT_UNIT, StatisticsMarks.WRONG_NUMBER_UNIT]]) : continue
            #print(left, right, repaired_sentence, sep='\n', end='\n\n')

            if args.texts:
                if isinstance(repaired_sentence, str):  # reporting repairs
                    output_file.write(left)
                    output_file.write('\t')
                    output_file.write(repaired_sentence)
                    output_file.write('\n')
                    print(left, repaired_sentence, sep='\t')
                else:
                    output_file.write(left)
                    output_file.write('\t')
                    output_file.write(right)
                    output_file.write('\n')
                    print(left, right, sep='\t')
            else:
                if isinstance(repaired_sentence, str):  # reporting repairs
                    print(left, right, repaired_sentence, sep='\n', end='\n\n')
                elif repaired_sentence is False:
                    print(left, right, "Unfixable sentence", sep='\n', end='\n\n')

    statistics_to_print = [(mark.name, statistics[mark.value]) for mark in StatisticsMarks]
    print(tabulate(statistics_to_print))


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
