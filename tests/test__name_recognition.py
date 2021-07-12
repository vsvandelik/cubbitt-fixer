from fixer._languages import Languages
from fixer._name_recognition import CapitalLettersBasedNameRecognition, NameTagApi


def test_get_names():
    sentence = "Pan Petr Novotný a Jana si koupili dům"
    correct_output = [
        ["Petr", "Novotný"],
        ["Jana"]
    ]

    assert CapitalLettersBasedNameRecognition.get_names(sentence, Languages.CS) == correct_output
    assert NameTagApi.get_names(sentence, Languages.CS) == correct_output


def test_get_names_only_person():
    sentence = "Petr Hudeček ze společnosti Metrostav, kterou najal Úřad pro věci majetkové, si zakoupil s manželkou Emou Novotnou linku metra."
    correct_output = [
        ["Petr", "Hudeček"],
        ["Emou", "Novotnou"]
    ]

    assert NameTagApi.get_names(sentence, Languages.CS) == correct_output


def test_get_names_only_person_en():
    sentence = "Petr has prepared weapons for Ukraine."
    correct_output = [
        ["Petr"]
    ]

    assert NameTagApi.get_names(sentence, Languages.EN) == correct_output
