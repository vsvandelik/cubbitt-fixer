from fixer._languages import Languages


def test_get_language():
    assert Languages.get_language("cs") == Languages.CS
    assert Languages.get_language("en") == Languages.EN
