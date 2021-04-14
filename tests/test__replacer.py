from fixer._languages import Languages
from fixer._replacer import Replacer
from fixer._units import units


def test_replace_unit_after_space():
    result = Replacer.replace_unit(
        "I went over the handlebars and flew a good 300 yards on the ground.",
        "300 yards",
        300,
        units.get_unit_by_word("yards", Languages.EN),
        units.get_unit_by_word("metres", Languages.EN))
    assert result == "I went over the handlebars and flew a good 300 metres on the ground."


def test_replace_unit_after_no_space():
    result = Replacer.replace_unit(
        "Abc def 300°F ghch ijk.",
        "300°F",
        300,
        units.get_unit_by_word("°F", Languages.EN),
        units.get_unit_by_word("°C", Languages.EN))
    assert result == "Abc def 300°C ghch ijk."


def test_replace_unit_before():
    result = Replacer.replace_unit(
        "Abc def 300 dollars ghch ijk.",
        "300 dollars",
        300,
        units.get_unit_by_word("dollars", Languages.EN),
        units.get_unit_by_word("CZK", Languages.EN))
    assert result == "Abc def CZK 300 ghch ijk."


def test_replace_unit_before_no_space():
    result = Replacer.replace_unit(
        "Abc def 300 dollars ghch ijk.",
        "300 dollars",
        300,
        units.get_unit_by_word("dollars", Languages.EN),
        units.get_unit_by_word("$", Languages.EN))
    assert result == "Abc def $300 ghch ijk."
