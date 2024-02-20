import requests
from datetime import datetime


def get_cryptos_data_from_coingecko():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    parameters = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
    }

    response = requests.get(url, params=parameters)
    data = response.json()

    cryptos_data = []

    for crypto in data:
        # Convert timestamp to readable date if 'ath_date' exists and is not None
        ath_date = datetime.fromisoformat(crypto['ath_date'][:-1]).strftime(
            '%Y-%m-%d %H:%M:%S') if crypto.get('ath_date') else 'N/A'

        crypto_data = {
            'name': crypto['name'],
            'symbol': crypto['symbol'],
            'current_price': crypto['current_price'],
            'ath': crypto['ath'],
            'ath_date': ath_date,
            'delta': crypto['ath'] - crypto['current_price']
        }
        cryptos_data.append(crypto_data)

    return cryptos_data


cryptos_data = get_cryptos_data_from_coingecko()

# Print column headers
print("Name\tSymbol\tCurrent Price\tATH\tATH Date\tDelta\tDelta (%)")

for crypto in cryptos_data:
    # Calculate the percentage difference
    if crypto['ath'] > 0:  # Prevent division by zero
        delta_percent = ((crypto['ath'] - crypto['current_price']) / crypto['current_price']) * 100
    else:
        delta_percent = 0  # Assign 0% if ATH is 0 to avoid division by zero error

    print(f"{crypto['name']}\t{crypto['symbol']}\t${crypto['current_price']:.2f}\t${crypto['ath']:.2f}\t{crypto['ath_date']}\t${crypto['delta']:.2f}\t{delta_percent:.2f}%")
