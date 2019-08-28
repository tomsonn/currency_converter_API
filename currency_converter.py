from flask import request, Flask, json
from exchange import Exchange, CurrencyCodeNotFoundError

app = Flask(__name__)


@app.route('/currency_converter', methods=['GET'])
def main():
    amount = request.args.get('amount')
    input_currency = request.args.get('input_currency')
    output_currency = request.args.get('output_currency')

    currency_converter = Exchange()

    try:
        converted_currencies = currency_converter.convert(amount, input_currency, output_currency)
    except CurrencyCodeNotFoundError as errcc:
        return errcc, 404
    except ValueError as errv:
        return errv, 404
    except TypeError as errt:
        return errt, 404

    print(json.dumps(converted_currencies, indent=4))


if __name__ == '__main__':
    app.run(debug=True)
