from fixer._exchange_rates import CNBExchangeRates


def test_get_rate_from_CZK():
    convertor = CNBExchangeRates({
        "USD": 25,
        "GBP": 35,
        "EUR": 45
    })

    assert convertor.get_rate("CZK", "USD", 25) == 1
    assert convertor.get_rate("CZK", "GBP", 35) == 1
    assert convertor.get_rate("CZK", "EUR", 45) == 1


def test_get_rate_to_CZK():
    convertor = CNBExchangeRates({
        "USD": 25,
        "GBP": 35,
        "EUR": 45
    })

    assert convertor.get_rate("USD", "CZK", 1) == 25
    assert convertor.get_rate("GBP", "CZK", 1) == 35
    assert convertor.get_rate("EUR", "CZK", 1) == 45


def test_get_rate_same_currency():
    convertor = CNBExchangeRates({
        "USD": 25,
        "GBP": 35,
        "EUR": 45
    })

    assert convertor.get_rate("CZK", "CZK", 1) == 1
    assert convertor.get_rate("USD", "USD", 1) == 1
    assert convertor.get_rate("GBP", "GBP", 1) == 1
    assert convertor.get_rate("EUR", "EUR", 1) == 1


def test_get_rate_not_CZK():
    convertor = CNBExchangeRates({
        "USD": 25,
        "GBP": 35,
        "EUR": 45
    })

    assert convertor.get_rate("USD", "GBP", 1) == (1 * 25) / 35
    assert convertor.get_rate("USD", "EUR", 1) == (1 * 25) / 45
    assert convertor.get_rate("GBP", "EUR", 1) == (1 * 35) / 45
    assert convertor.get_rate("GBP", "USD", 1) == (1 * 35) / 25
    assert convertor.get_rate("EUR", "GBP", 1) == (1 * 45) / 35
    assert convertor.get_rate("EUR", "USD", 1) == (1 * 45) / 25
