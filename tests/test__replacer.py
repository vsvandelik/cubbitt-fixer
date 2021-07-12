from fixer._finder import NumberUnitFinderResult
from fixer._languages import Languages
from fixer._replacer import Replacer
from fixer._units import units


def test_replace_unit_after_space():
    result = Replacer.replace_unit(
        "I went over the handlebars and flew a good 300 yards on the ground.",
        NumberUnitFinderResult(300, units.get_unit_by_word("metrů", Languages.CS), False, "300 metrů"),
        NumberUnitFinderResult(300, units.get_unit_by_word("yards", Languages.EN), False, "300 yards"),
        units.get_unit_by_word("metres", Languages.EN),
        Languages.EN)
    assert result == "I went over the handlebars and flew a good 300 metres on the ground."


def test_replace_unit_after_no_space():
    result = Replacer.replace_unit(
        "Abc def 300°F ghch ijk.",
        NumberUnitFinderResult(300, units.get_unit_by_word("°C", Languages.CS), False, "300°C"),
        NumberUnitFinderResult(300, units.get_unit_by_word("°F", Languages.EN), False, "300°F"),
        units.get_unit_by_word("°C", Languages.EN),
        Languages.EN)
    assert result == "Abc def 300°C ghch ijk."


def test_replace_unit_before():
    result = Replacer.replace_unit(
        "Abc def 300 dollars ghch ijk.",
        NumberUnitFinderResult(300, units.get_unit_by_word("korun", Languages.CS), False, "300 korun"),
        NumberUnitFinderResult(300, units.get_unit_by_word("dollars", Languages.EN), False, "300 dollars"),
        units.get_unit_by_word("CZK", Languages.EN),
        Languages.EN)
    assert result == "Abc def CZK 300 ghch ijk."


def test_replace_unit_before_no_space():
    result = Replacer.replace_unit(
        "Abc def 300 dollars ghch ijk.",
        NumberUnitFinderResult(300, units.get_unit_by_word("korun", Languages.CS), False, "300 korun"),
        NumberUnitFinderResult(300, units.get_unit_by_word("dollars", Languages.EN), False, "300 dollars"),
        units.get_unit_by_word("$", Languages.EN),
        Languages.EN)
    assert result == "Abc def $300 ghch ijk."


def test_replace_number():
    result = Replacer.replace_number(
        "Abc def 300 dollars ghch ijk.",
        NumberUnitFinderResult(500, units.get_unit_by_word("dolarů", Languages.CS), False, "500 dolarů"),
        NumberUnitFinderResult(300, units.get_unit_by_word("dollars", Languages.EN), False, "300 dollars"),
        Languages.EN,
        "300"
    )
    assert result == "Abc def 500 dollars ghch ijk."

def test_replace_number_with_scaling():
    n = NumberUnitFinderResult(123456.789, units.get_unit_by_word("dolarů", Languages.CS), False, "123 456 789 dolarů")
    n.add_scaling(1000)

    result = Replacer.replace_number(
        "Abc def 500.1 dollars ghch ijk.",
        n,
        NumberUnitFinderResult(500.1, units.get_unit_by_word("dollars", Languages.EN), False, "500.1 dollars"),
        Languages.EN,
        "500.1"
    )
    assert result == "Abc def 123,456.789 thousand dollars ghch ijk."


def test_replace_unit_number_cs():
    result = Replacer.replace_unit_number(
        "Abc def 500,1 korun ghch ijk.",
        NumberUnitFinderResult(500.1, units.get_unit_by_word("crowns", Languages.EN), False, "500.1 crowns"),
        NumberUnitFinderResult(500.1, units.get_unit_by_word("korun", Languages.CS), False, "500,1 korun"),
        1234.123,
        units.get_unit_by_word("dolarů", Languages.CS),
        Languages.CS
    )
    assert result == "Abc def 1 234,1 dolarů ghch ijk."


def test_replace_unit_number():
    result = Replacer.replace_unit_number(
        "Abc def 500.1 crowns ghch ijk.",
        NumberUnitFinderResult(500.1, units.get_unit_by_word("korun", Languages.CS), False, "500,1 korun"),
        NumberUnitFinderResult(500.1, units.get_unit_by_word("crowns", Languages.EN), False, "500.1 crowns"),
        123456789,
        units.get_unit_by_word("dollars", Languages.EN),
        Languages.EN
    )
    assert result == "Abc def 123,460,000 dollars ghch ijk."


def test_replace_unit_number_scaling():
    n = NumberUnitFinderResult(500.1, units.get_unit_by_word("korun", Languages.CS), False, "500,1 korun")
    n.add_scaling(1)

    result = Replacer.replace_unit_number(
        "Abc def 500.1 crowns ghch ijk.",
        n,
        NumberUnitFinderResult(500.1, units.get_unit_by_word("crowns", Languages.EN), False, "500.1 crowns"),
        123456789,
        units.get_unit_by_word("dollars", Languages.EN),
        Languages.EN
    )
    assert result == "Abc def 123.46 million dollars ghch ijk."
