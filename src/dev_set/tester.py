import sys
from os import listdir
from os.path import isfile, join

from fixer import *
from tabulate import tabulate

devset_languages = ["cs-en", "en-cs"]

default_config = {
    'source_lang': 'cs',
    'target_lang': 'en',
    'aligner': 'fast_align',
    'lemmatizator': 'udpipe_offline',
    'names_tagger': 'nametag',
    'mode': 'fixing',
    'base_tolerance': 0.1,
    'approximately_tolerance': 0.1,
    'target_units': ['imperial', 'USD', 'F'],
    'exchange_rates': 'cnb',
    'tools': ['separators', 'units']
}


def report_result(data):
    print(tabulate(data, headers=["File", "Accuracy", "Precision", "Recall"]))


def meters_metres_correction(sentence: str):
    return sentence.replace("metre", "meter")


def process_sentences_in_file(folder_path: str, filename: str, fixer_instance: Fixer, report_file):
    true_positive = 0  # correctly fixed sentence
    true_negative = 0  # not change correct sentence
    false_positive = 0  # wrongly fixed sentence
    false_negative = 0  # change correct sentence

    with open(join(folder_path, filename), encoding="utf-8") as input_file:
        for original_sentence in input_file:
            # original_sentence = input_file.readline()
            translated_sentence = input_file.readline()
            correct_sentence = input_file.readline()
            input_file.readline()  # remove space

            result_sentence = None

            # Check fix broken sentence
            result, _ = fixer_instance.fix(original_sentence, translated_sentence)
            if isinstance(result, bool):  # True or False
                result_sentence = translated_sentence
            elif result:
                result_sentence = result

            if isinstance(result, str) and meters_metres_correction(result) == correct_sentence:
                true_positive += 1
            else:
                false_positive += 1
                report_file.writelines([original_sentence, translated_sentence, result_sentence, correct_sentence, '\n'])

            # Check leave correct sentence
            result, _ = fixer_instance.fix(original_sentence, correct_sentence)
            if result is True:
                true_negative += 1
            else:
                false_negative += 1
                result = "UNFIXABLE SENTENCE\n" if result is False else result
                report_file.writelines([original_sentence, correct_sentence, result, correct_sentence, '\n'])

    return true_positive, true_negative, false_positive, false_negative


def run_test(folder_name: str, report_file: str):
    devset_files = [file for file in listdir(folder_name) if isfile(join(folder_name, file)) and file != "README.md"]

    languages = folder_name.split("-")
    default_config['source_lang'] = languages[0]
    default_config['target_lang'] = languages[1]
    configuration = FixerConfigurator()
    configuration.load_from_dict(default_config)
    fixer_instance = Fixer(configuration)

    results = []
    true_positive, true_negative, false_positive, false_negative = 0, 0, 0, 0

    for devset_file in devset_files:
        report_file.write(devset_file + "\n")
        tp, tn, fp, fn = process_sentences_in_file(folder_name, devset_file, fixer_instance, report_file)
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if tp + fp != 0 else "NaN"
        recall = tp / (tp + fn) if tp + fn != 0 else "NaN"
        results.append([devset_file, accuracy, precision, recall])
        true_positive += tp
        true_negative += tn
        false_positive += fp
        false_negative += fn

    accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    results.append(["SUMMARY", accuracy, precision, recall])
    report_result(results)
    print(f"\nsentences count: {true_positive + true_negative + false_positive + false_negative} ({(true_positive + true_negative + false_positive + false_negative) // 2})")


if __name__ == "__main__":
    sys.argv.pop(0)  # remove program name

    language_direction = [sys.argv.pop(0)] if len(sys.argv) > 0 else devset_languages
    output_file = sys.argv.pop(0) if len(sys.argv) > 0 else "test_report.txt"

    with open(output_file, "w", encoding="utf-8") as report_file:
        for direction in language_direction:
            print(direction, ":", sep="")
            run_test(direction, report_file)
