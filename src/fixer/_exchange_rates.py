from abc import ABC, abstractmethod
from datetime import date
from typing import Dict

import requests


class CNBCommunicationException(Exception):
    """Exception indicating problem with loading the exchange rates."""
    pass


class ExchangeRatesInterface(ABC):
    """Base interface for getting the exchange rate between two currencies."""

    @abstractmethod
    def get_rate(self, original_currency: str, exchanged_currency: str, amount: float) -> float:
        pass


class CNBExchangeRates(ExchangeRatesInterface):
    """Wrapper for communicating with Czech national bank for getting the exchange rates

    It can get 'hard-coded' exchange rates from the caller which will override
    rates from the national bank.

    All rates are saved with respect to czech crown.
    """

    _CNB_API_RATES = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    _UNITS_CURRENCIES = ['CZK', 'GBP', 'EUR', 'USD']

    def __init__(self, predefined_rates: Dict[str, float] = None):
        """
        :param predefined_rates: Dictionary of exchange rates given by configuration
        """
        self.rates = CNBExchangeRates.load_rates()

        if predefined_rates:
            for abbr, rate in predefined_rates.items():
                if abbr in self.rates:
                    self.rates[abbr] = rate

    @staticmethod
    def load_rates():
        """Load exchange rates from the Czech National Bank.

        Provide a http request to website of CNB and returns plain text
        file containing the exchange rates of czech crowns to word currencies.

        Response from the server has following format (starting third line):
        `country|currency|amount|code|rate`

        The server accept the date to get actual rates for given date. We provide
        date of using the package (regardless weekends - on weekend date the CNB
        returns rates of last working day).

        :return: Dictionary with currencies codes as keys and rates to czech crown as value
        """
        complete_url = "{}?date={}".format(CNBExchangeRates._CNB_API_RATES, date.today().strftime("%d.%m.%Y"))
        response = requests.get(complete_url)

        if response.status_code != 200:
            raise CNBCommunicationException('It was not possible to connect to the CNB official website.')

        rates = {}

        for line in response.text.splitlines()[2:]:
            _, _, amount, abbr, rate = line.split('|')
            if abbr in CNBExchangeRates._UNITS_CURRENCIES:
                amount = int(amount)
                rate = float(rate.replace(',', '.'))
                if amount != 1:
                    rate /= amount
                rates[abbr] = rate

        return rates

    def get_rate(self, original_currency: str, exchanged_currency: str, amount: float) -> float:
        """Returns recalculated amount of money from original currency to target one

        Recalculating is provided by currencies given from user or the CNB.

        The input amount of money is always firstly converted to czech crown and then
        converted to target currency. That can provide little inaccuracy of final amount.

        :param original_currency: Code of currency of param amount
        :param exchanged_currency: Code of currency to be converted to
        :param amount: Amount of money to be converted
        :return: Converted amount of money to target currency
        """
        if original_currency == exchanged_currency:
            return amount

        if original_currency != 'CZK':
            amount *= self.rates[original_currency]

        if exchanged_currency != 'CZK':
            amount /= self.rates[exchanged_currency]

        return amount


exchange_rates_convertor = CNBExchangeRates()


def get_exchange_rates_convertors_list():
    return {
        'cnb': CNBExchangeRates
    }


def get_default_exchange_rates_convertor():
    return 'cnb'
