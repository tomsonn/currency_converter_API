import requests
from requests import exceptions


class CurrencyCodeNotFoundError(Exception):
    pass


class Exchange:

    def __init__(self):
        self.api_url = 'http://www.localeplanet.com/api/auto/currencymap.json'

    def convert(self, amount, input_currency, output_currency):
        if float(amount) < 0.0:
            raise ValueError('Amount of money you want to exchange have to be positive number!')

        if input_currency is None:
            raise TypeError('Input currency can\'t be None!')

        response = self.create_request(self.api_url, 'currency_code')
        currency_database = response.json()

        input_currency_id = self.get_currency_id(currency_database, input_currency)
        if input_currency_id is None:
            raise CurrencyCodeNotFoundError(f'We couldn\'t find currency {input_currency} in our database!')

        if output_currency is not None:
            output_currency_id = self.get_currency_id(currency_database, output_currency)
            if output_currency_id is None:
                raise CurrencyCodeNotFoundError(f'We couldn\'t find currency {output_currency} in our database!')

            return self.create_conversion_structure(amount, input_currency_id, output_currency_id)
        else:
            return self.create_conversion_structure(amount, input_currency_id)

    def create_request(self, api_url, request_type):

        try:
            response = requests.session().get(api_url)
            response.raise_for_status()
        except exceptions.RequestException as errh:
            if request_type == 'currency_code':
                print(f'We couldn\'t check for currency codes!: {errh}')
                return 404
            else:
                print(f'We couldn\'t convert desired currencies!: {errh}')
                return 404

        return response

    def get_currency_id(self, currency_database, currency):
        # User's input is 3 letter currency code
        # Testing whether code exist in database or not
        if currency in currency_database:
            return currency_database[currency]['code']

        # If not, check for symbol occurrence
        for currency_row in currency_database.values():
            if currency_row['symbol'] == currency:
                return currency_row['code']

        # Lastly check for native symbol of currency. For example we can't find Yen ¥ in symbols, but in native symbols.
        # We need it graded, because native symbols have the lowest priority as they contains duplicates.
        for currency_row in currency_database.values():
            if currency_row['symbol_native'] == currency:
                return currency_row['code']

        # If we found nothing, return None
        return None

    def get_conversion_rates(self, input_currency_id, output_currency_id=None):
        if output_currency_id is not None:
            converter_url = f'https://api.ratesapi.io/api/latest?base={input_currency_id}&symbols={output_currency_id}'
        else:
            converter_url = f'https://api.ratesapi.io/api/latest?base={input_currency_id}'

        response = self.create_request(converter_url, 'conversion_rate')

        return response.json()['rates']

    def create_conversion_structure(self, amount, input_currency, output_currencies=None):
        input_currency_structure = {
            'amount': amount,
            'currency': input_currency
        }

        output_against_single_unit = self.get_conversion_rates(input_currency, output_currencies)
        output_converted_currencies = {key: round(value * float(amount), 2) for key, value in output_against_single_unit.items()}

        converted_currencies = {
            'input': input_currency_structure,
            'output': output_converted_currencies
        }

        return converted_currencies