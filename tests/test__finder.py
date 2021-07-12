from fixer._finder import Finder, NumberUnitFinderResult
from fixer._languages import Languages
from fixer._lemmatization import UDPipeOnline
from fixer._units import units


def test_find_number_unit_pairs_cs():
    pairs = Finder.find_number_unit_pairs("Koupil jsem si 25 domů za 100 tisíc korun českých.", Languages.CS)

    r1 = NumberUnitFinderResult(25, None, False, "25")
    r2 = NumberUnitFinderResult(100, units.get_unit_by_word("korun českých", Languages.CS), False, "100 tisíc korun českých")
    r2.add_scaling(1000)

    compare_number_unit_finder_result(r1, pairs[0])
    compare_number_unit_finder_result(r2, pairs[1])


def test_find_number_unit_pairs_approximately():
    pairs = Finder.find_number_unit_pairs("Koupil jsem asi 3 metry provazu", Languages.CS)

    r1 = NumberUnitFinderResult(3, units.get_unit_by_word("metry", Languages.CS), True, "3 metry")

    compare_number_unit_finder_result(r1, pairs[0])


def test_find_number_unit_pairs_separators():
    pairs = Finder.find_number_unit_pairs("Stál 54 123 456,788 dolarů, později dokonce 54.123.456,789 dolarů a nakonec stál 54123456 USD", Languages.CS)

    r1 = NumberUnitFinderResult(54123456.788, units.get_unit_by_word("dolarů", Languages.CS), False, "54 123 456,788 dolarů")
    r2 = NumberUnitFinderResult(54123456.789, units.get_unit_by_word("dolarů", Languages.CS), False, "54.123.456,789 dolarů")
    r3 = NumberUnitFinderResult(54123456, units.get_unit_by_word("USD", Languages.CS), False, "54123456 USD")

    compare_number_unit_finder_result(r1, pairs[0])
    compare_number_unit_finder_result(r2, pairs[1])
    compare_number_unit_finder_result(r3, pairs[2])


def test_find_number_unit_pairs_skipping_hours_sports():
    pairs = Finder.find_number_unit_pairs("Bylo 12:23 a skore bylo 5-0.", Languages.CS)

    assert len(pairs) == 0


def test_find_number_unit_pairs_modifiers():
    pairs = Finder.find_number_unit_pairs("Violence along the 900-mile border between the two states has increased significantly in recent days.", Languages.EN)

    r1 = NumberUnitFinderResult(900, units.get_unit_by_word("mile", Languages.EN), False, "900-mile")
    r1.modifier = True

    compare_number_unit_finder_result(r1, pairs[0])


def test_find_word_number_unit_cs():
    sentence = "Koupil asi dvacet tisíc metrů dlouhý provaz a udělal tisíc koleček na 5 metrů."
    pairs = Finder.find_word_number_unit(sentence, Languages.CS, UDPipeOnline.get_lemmatization(sentence, Languages.CS))

    r1 = NumberUnitFinderResult(20, units.get_unit_by_word("metrů", Languages.CS), True, "dvacet tisíc metrů")
    r1.add_scaling(1000)
    r1.number_as_string = "dvacet tisíc"
    r2 = NumberUnitFinderResult(1, None, False, "tisíc")
    r2.add_scaling(1000)
    r2.number_as_string = "tisíc"

    compare_number_unit_finder_result(r1, pairs[0])
    compare_number_unit_finder_result(r2, pairs[1])


def test_find_word_number_unit_en():
    sentence = "He bought a twenty one kilograms of chocolate."
    pairs = Finder.find_word_number_unit(sentence, Languages.EN, UDPipeOnline.get_lemmatization(sentence, Languages.EN))

    r1 = NumberUnitFinderResult(21, units.get_unit_by_word("kilograms", Languages.EN), False, "twenty one kilograms")
    r1.number_as_string = "twenty one"

    compare_number_unit_finder_result(r1, pairs[0])


def compare_number_unit_finder_result(r1, r2):
    assert r1.number == r2.number
    assert r1.unit == r2.unit
    assert r1.approximately == r2.approximately
    assert r1.text_part == r2.text_part
    assert r1.scaling == r2.scaling
    assert r1.number_as_string == r2.number_as_string
    assert r1.modifier == r2.modifier
