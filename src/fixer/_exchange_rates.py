from abc import ABC, abstractmethod
from datetime import date

import requests
from ._units import Unit, UnitCategories


class CNBCommunicationException(Exception):
    pass


class ExchangeRatesInterface(ABC):

    @abstractmethod
    def get_rate(self, original_currency: Unit, exchanged_currency: Unit, amount: float) -> float:
        pass


class Rate:
    def __init__(self, abbr: str, rate: float):
        self.abbr = abbr
        self.rate = rate


class CNBExchangeRates(ExchangeRatesInterface):
    _CNB_API_RATES = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    _UNITS_CURRENCIES_TABLE = {
        UnitCategories.CZK: 'CZK',
        UnitCategories.GBP: 'GBP',
        UnitCategories.EUR: 'EUR',
        UnitCategories.USD: 'USD'
    }

    def __init__(self, predefined_rates=None):
        self.rates = CNBExchangeRates.load_rates()

        if predefined_rates:
            for abbr, rate in predefined_rates.items():
                if abbr in self.rates.keys():
                    self.rates[abbr] = rate

    @staticmethod
    def load_rates():
        complete_url = "{}?date={}".format(CNBExchangeRates._CNB_API_RATES, date.today().strftime("%d.%m.%Y"))
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise CNBCommunicationException('It was not possible to connect to the CNB official website.')

        rates = {}

        for line in response.text.splitlines()[2:]:
            _, _, amount, abbr, rate = line.split('|')
            if abbr in CNBExchangeRates._UNITS_CURRENCIES_TABLE.values():
                amount = int(amount)
                rate = float(rate.replace(',', '.'))
                if amount != 1:
                    rate /= amount
                rates[abbr] = Rate(abbr, rate)

        return rates

    def get_rate(self, original_currency: Unit, exchanged_currency: Unit, amount: float) -> float:
        if original_currency == exchanged_currency:
            return amount

        if original_currency != UnitCategories.CZK:
            amount *= self.rates[CNBExchangeRates._UNITS_CURRENCIES_TABLE[original_currency]].rate

        if exchanged_currency != UnitCategories.CZK:
            amount /= self.rates[CNBExchangeRates._UNITS_CURRENCIES_TABLE[exchanged_currency]].rate

        return amount
