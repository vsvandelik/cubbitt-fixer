from fixer._units import *


def test_get_best_unit_for_converted_number():
    assert UnitsConvertors.get_best_unit_for_converted_number(5000, UnitCategories.M, Languages.EN, units.get_unit_by_word("metrů", Languages.CS), units.get_unit_by_word("inches", Languages.EN)) == (5.0, units.get_unit_by_word("kilometers", Languages.EN))


def test_length_convertor():
    num, category = UnitsConvertors.length_convertor(5000, UnitCategories.M, [UnitsSystem.IMPERIAL])

    assert round(num) == 16404
    assert category == UnitCategories.FT

    num, category = UnitsConvertors.length_convertor(5000, UnitCategories.FT, [UnitsSystem.SI])

    assert round(num) == 1524
    assert category == UnitCategories.M


def test_weight_convertor():
    num, category = UnitsConvertors.weight_convertor(5000, UnitCategories.G, [UnitsSystem.IMPERIAL])

    assert round(num) == 11
    assert category == UnitCategories.LB

    num, category = UnitsConvertors.weight_convertor(5000, UnitCategories.LB, [UnitsSystem.SI])

    assert round(num) == 2267962
    assert category == UnitCategories.G


def test_area_convertor():
    num, category = UnitsConvertors.area_convertor(5000, UnitCategories.M2, [UnitsSystem.IMPERIAL])

    assert round(num) == 53820
    assert category == UnitCategories.FT2

    num, category = UnitsConvertors.area_convertor(5000, UnitCategories.FT2, [UnitsSystem.SI])

    assert round(num) == 465
    assert category == UnitCategories.M2


def test_volume_convertor():
    num, category = UnitsConvertors.volume_convertor(5000, UnitCategories.M3, [UnitsSystem.IMPERIAL])

    assert round(num) == 176575
    assert category == UnitCategories.FT3

    num, category = UnitsConvertors.volume_convertor(5000, UnitCategories.FT3, [UnitsSystem.SI])

    assert round(num) == 142
    assert category == UnitCategories.M3


def test_temperature_convertor():
    num, category = UnitsConvertors.temperature_convertor(20, UnitCategories.C, [UnitsSystem.F])

    assert round(num) == 68
    assert category == UnitCategories.F

    num, category = UnitsConvertors.temperature_convertor(20, UnitCategories.F, [UnitsSystem.C])

    assert round(num) == -7
    assert category == UnitCategories.C


def test_number_pass_numbers_validity_float():
    assert Unit.number_pass_numbers_validity([(None, -1), (1, None), float], 25.3)


def test_number_pass_numbers_validity_exact():
    assert Unit.number_pass_numbers_validity([-4, -3, -2, 2, 3, 4], -3)


def test_number_pass_numbers_validity_interval():
    assert Unit.number_pass_numbers_validity([(None, -4), (4, None)], 125)


def test_get_correct_unit():
    assert units.get_correct_unit(Languages.CS, 125, units.get_unit_by_word("meter", Languages.EN)) == units.get_unit_by_word("metrů", Languages.CS)


def test_get_correct_unit_abbreviation():
    assert units.get_correct_unit(Languages.EN, 125, units.get_unit_by_word("km", Languages.CS)) == units.get_unit_by_word("km", Languages.EN)


def test_get_correct_unit_abbreviation_forced():
    assert units.get_correct_unit(Languages.EN, 125, units.get_unit_by_word("kilometrů", Languages.CS), abbreviation=True) == units.get_unit_by_word("km", Languages.EN)


def test_get_correct_unit_abbreviation_forced_negative():
    assert units.get_correct_unit(Languages.EN, 125, units.get_unit_by_word("km", Languages.CS), abbreviation=False) == units.get_unit_by_word("kilometers", Languages.EN)


def test_convert_number():
    num, unit = units.convert_number(Languages.CS, [UnitsSystem.SI], 123, units.get_unit_by_word("feet", Languages.EN), units.get_unit_by_word("stop", Languages.CS))

    assert round(num) == 37
    assert unit == units.get_unit_by_word("metru", Languages.CS)


def test_convert_number_with_changing_unit_category():
    num, unit = units.convert_number(Languages.EN, [UnitsSystem.IMPERIAL], 456786, units.get_unit_by_word("metrů", Languages.CS), units.get_unit_by_word("m", Languages.EN))

    assert round(num) == 284
    assert unit == units.get_unit_by_word("miles", Languages.EN)


def test_convert_to_base_in_category():
    assert units.convert_to_base_in_category(units.get_unit_by_word("kilogramů", Languages.CS), 12) == 12000


def test_convert_to_base_in_another_system():
    num = units.convert_to_base_in_another_system(units.get_unit_by_word("centimetrů", Languages.CS), 1201, UnitCategories.FT)
    assert round(num) == 39
