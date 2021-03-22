import json
import sys
from typing import Tuple, List

import requests
import tabulate


class AlignerApiException(Exception):
    """Exception raised when the aligner api was not able to connect to the server."""
    pass


class AlignerApi:
    """Support class for communicating with the aligner server.

    It uses predefined alignment server running at UFAL, MFF. The server uses
    fast_align tool for word-alignment with CzEng2 as dataset.
    """
    ALIGNER_URL = 'https://quest.ms.mff.cuni.cz/ptakopet-mt380/align/en-cs'

    @staticmethod
    def get_alignment(src_text: str, trg_text: str) -> List[Tuple[str, str]]:
        """Static method for getting a word-alignment of pair of english and czech sentences.

        Based on given sentences it communicate with external word-aligner tool, which
        returns the pairs of matching indexes and tokenized input sentences.

        :param src_text: Sentence in english
        :param trg_text: Sentence in czech
        :raises AlignerApiException: Exception raises when it was not possible to connect to the server
        :return: List of tuples of matching words, first word is in english, second in czech
        """
        payload = json.dumps({
            'src_text': src_text,
            'trg_text': trg_text})
        headers = {'Content-type': 'application/json'}
        response = requests.post(AlignerApi.ALIGNER_URL, headers=headers, data=payload)

        if response.status_code != 200:
            raise AlignerApiException('Aligner was not able to connect to the alignment server.')
        else:
            parsed_response = json.loads(response.content)
            words = []
            for pair in parsed_response['alignment'].split():
                split_pair = pair.split('-')
                left_idx = int(split_pair[0])
                right_idx = int(split_pair[1])
                words.append((parsed_response['src_tokens'][left_idx], parsed_response['trg_tokens'][right_idx]))

            return words


if __name__ == '__main__':
    for line in sys.stdin.readlines():
        if line == '':
            continue

        parts = line.split('\t')
        source_text = parts[0]
        target_text = parts[1]

        word_pairs = AlignerApi.get_alignment(source_text, target_text)
        print(word_pairs)
        print(tabulate.tabulate(word_pairs, headers=['SRC', 'TRG']))
