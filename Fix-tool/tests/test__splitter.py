import pytest

from fixer._languages import Languages
from fixer._splitter import StringToNumberUnitConverter as Splitter
from fixer._units import units


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_number_before(language):
    number, unit = Splitter.split_number_unit("250 km", language)
    assert number == 250 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_number_before_without_space(language):
    number, unit = Splitter.split_number_unit("250km", language)
    assert number == 250 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_number_before_with_dash(language):
    number, unit = Splitter.split_number_unit("250-km", language)
    assert number == 250 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language, number_string", [(Languages.CS, "250.000"), (Languages.EN, "250,000")])
def test_split_number_unit_number_thousands(language, number_string):
    number, unit = Splitter.split_number_unit(f"{number_string} km", language)
    assert number == 250000 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language, number_string", [(Languages.CS, "250,123"), (Languages.EN, "250.123")])
def test_split_number_unit_number_decimal(language, number_string):
    number, unit = Splitter.split_number_unit(f"{number_string} km", language)
    assert number == 250.123 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language, number_string", [(Languages.CS, "250-000"), (Languages.EN, "250-000")])
def test_split_number_unit_custom_separator(language, number_string):
    number, unit = Splitter.split_number_unit(f"{number_string} km", language, custom_separator='-')
    assert number == 250.000 and unit == units.get_unit_by_word("km", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_number_after(language):
    number, unit = Splitter.split_number_unit("$250", language)
    assert number == 250 and unit == units.get_unit_by_word("$", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_number_after_space(language):
    number, unit = Splitter.split_number_unit("$ 250", language)
    assert number == 250 and unit == units.get_unit_by_word("$", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_multiple_sentences(language):
    number, unit = Splitter.split_number_unit("Back in 1892, 250 kilometres", language)
    assert number == 250 and unit == units.get_unit_by_word("kilometres", language)


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_nonexisting_unit(language):
    number, unit = Splitter.split_number_unit("250 abc", language)
    assert number == 250 and unit == None


@pytest.mark.parametrize("language", Languages.get_languages_list())
def test_split_number_unit_unparsable_number(language):
    with pytest.raises(ValueError):
        number, unit = Splitter.split_number_unit("250.45.2,25,12 km", language)
