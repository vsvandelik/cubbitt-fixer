import argparse
from fixer import Fixer

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Name of file to be checked")
parser.add_argument("source_lang", help="Label of source language of file (sentences on left)")
parser.add_argument("target_lang", help="Label of translated language of file (sentences on right)")

parser.add_argument("--approximately", action="store_true", default=False,
                    help="Whenever the numbers need to be precise")
parser.add_argument("--recalculate", action="store_true", default=False,
                    help="Whenever the numbers should be recalculated to new units")

parser.add_argument("--limit", default=100000, type=int, help="Count of sentences to be checked")
parser.add_argument("--offset", default=0, type=int, help="Offset of sentences to be checked")


def main(args):
    fixer = Fixer(args)
    results = []

    with open(args.file, "r", encoding="utf8") as input_file:
        for _ in range(args.offset):  # skipping the offset
            next(input_file)

        last = None
        for line in input_file:  # checking the limit
            args.limit -= 1
            if args.limit == 0:
                break

            if line.isspace():
                continue

            left, right = line.split('\t')

            if left == last:  # skipping same sentences
                continue
            last = left

            left = left.strip()
            right = right.strip()

            repaired_sentence = fixer.fix(left, right)

            if isinstance(repaired_sentence, str):  # reporting repairs
                print(left, right, repaired_sentence, sep='\n', end='\n\n')
            elif repaired_sentence is False:
                print(left, right, "Unfixable sentence", sep='\n', end='\n\n')


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
