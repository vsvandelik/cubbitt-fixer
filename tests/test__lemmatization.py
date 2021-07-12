from fixer._languages import Languages
from fixer._lemmatization import UDPipeOffline, UDPipeOnline


def test_get_sentences_split():
    input_sentences = "Koupil si dům. Velmi drahý dům. Žil v něm celý život.\nAž do smrti.\n\nOna měla také dům. Žila v něm také velmi dlouho.\nAle než až do smrti."
    correct_output = [
        ["Koupil si dům.", "Velmi drahý dům.", "Žil v něm celý život.", "Až do smrti."],
        ["Ona měla také dům.", "Žila v něm také velmi dlouho.", "Ale než až do smrti."]
    ]

    assert UDPipeOnline.get_sentences_split(input_sentences, Languages.CS) == correct_output
    assert UDPipeOffline().get_sentences_split(input_sentences, Languages.CS) == correct_output


def test_get_lemmatization():
    input_sentences = "Když si za sebe sedne 185 centimetrů vysoký řidič, stále mu zbývá dobrých deset centimetrů před koleny."

    assert UDPipeOnline.get_sentences_split(input_sentences, Languages.CS) == UDPipeOffline().get_sentences_split(input_sentences, Languages.CS)
