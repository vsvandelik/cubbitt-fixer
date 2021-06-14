import pytest

from fixer._languages import Languages
from fixer._words_to_numbers_converter import WordsNumbersConverter


def test_convert_9():
    assert WordsNumbersConverter.convert(["devět"], Languages.CS) == 9


def test_convert_28():
    assert WordsNumbersConverter.convert(["dvacet", "osm"], Languages.CS) == 28


def test_convert_53():
    assert WordsNumbersConverter.convert(["tři", "a", "padesát"], Languages.CS) == 53


def test_convert_167():
    assert WordsNumbersConverter.convert(["sto", "šedesát", "sedm"], Languages.CS) == 167


def test_convert_1010():
    assert WordsNumbersConverter.convert(["tisíc", "deset"], Languages.CS) == 1010


def test_convert_1591():
    assert WordsNumbersConverter.convert(["tisíc", "pět", "set", "devadesát", "jedna"], Languages.CS) == 1591


def test_convert_85000():
    assert WordsNumbersConverter.convert(["pět", "a", "osmdesát", "tisíc"], Languages.CS) == 85000


def test_convert_150000():
    assert WordsNumbersConverter.convert(["sto", "padesát", "tisíc"], Languages.CS) == 150000


def test_convert_15000000():
    assert WordsNumbersConverter.convert(["sto", "patnáct", "milionů"], Languages.CS) == 115000000


def test_convert_5987542():
    assert WordsNumbersConverter.convert(["pět", "milion", "devět", "set", "osmdesát", "sedm", "tisíc", "pět", "set", "čtyřicet", "dva"], Languages.CS) == 5987542


def test_convert_110():
    assert WordsNumbersConverter.convert(["sto", "deset"], Languages.CS) == 110


def test_convert_1150():
    assert WordsNumbersConverter.convert(["tisíc", "sto", "padesát"], Languages.CS) == 1150
