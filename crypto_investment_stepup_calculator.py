import argparse
import datetime
import requests
import time

DEFAULT_API_REQUEST_DELAY = 4  # Delay in seconds between each API request


def get_crypto_ids(delay):
    response = requests.get("https://api.coingecko.com/api/v3/coins/list")
    time.sleep(delay)  # Delay after the first request
    if response.status_code == 200:
        crypto_list = response.json()
        crypto_ids = {crypto["symbol"]: crypto["id"] for crypto in crypto_list}
        return crypto_ids
    else:
        print("Failed to retrieve cryptocurrency list.")
        return {}


def get_current_price(crypto_id, delay):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    response = requests.get(url)
    time.sleep(delay)  # Delay before each request
    if response.status_code == 200:
        data = response.json()
        if crypto_id in data:
            return data[crypto_id]["usd"]
        else:
            print(f"Failed to retrieve current price for {crypto_id}.")
    else:
        print(f"Failed to retrieve current price for {crypto_id}.")
    return None


def calculate_investments(start_date, end_date=None, step_percentage=1, amount=1, ticker='BTC', ticker_id=None, delay=DEFAULT_API_REQUEST_DELAY):
    if not end_date:
        end_date = datetime.datetime.now().strftime('%d-%m-%Y')

    start_date = datetime.datetime.strptime(
        start_date, '%d-%m-%Y')  # Update date format to dd-mm-yyyy
    end_date = datetime.datetime.strptime(
        end_date, '%d-%m-%Y')  # Update date format to dd-mm-yyyy

    total_crypto = amount / get_current_price(ticker_id, delay)
    total_investment = amount

    url = f"https://api.coingecko.com/api/v3/coins/{ticker_id}/market_chart/range?vs_currency=usd&from={int(start_date.timestamp())}&to={int(end_date.timestamp())}"
    print(f"\nRequesting URL: {url}\n")

    response = requests.get(url)
    time.sleep(delay)

    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices')
        if prices:
            last_purchase_date = start_date - datetime.timedelta(days=1)
            for i in range(len(prices)):
                timestamp = prices[i][0]
                price_value = prices[i][1]
                current_date = datetime.datetime.fromtimestamp(
                    timestamp // 1000)  # Convert from milliseconds to seconds
                if current_date.date() > last_purchase_date.date():
                    # Check if the price has increased by the step percentage
                    if price_value >= (1 + step_percentage / 100) * total_investment / total_crypto:
                        crypto_amount = amount / price_value
                        total_crypto += crypto_amount
                        total_investment += amount
                        last_purchase_date = current_date
        else:
            print(
                f"Unable to retrieve prices for {ticker} in the specified range.")
    else:
        print(
            f"Unable to retrieve prices for {ticker} in the specified range.")

    return total_crypto, total_investment


def main():
    parser = argparse.ArgumentParser(
        description='Calculate the result of step-up investments into a specific cryptocurrency.')
    parser.add_argument(
        '-s', '--start', help='Start date for the investment strategy in dd-mm-yyyy format.', required=True)
    parser.add_argument(
        '-e', '--end', help='End date for the investment strategy in dd-mm-yyyy format. If not provided, the current date will be used.')
    parser.add_argument('-p', '--step_percentage',
                        help='Step percentage for each purchase. For example, 1 for 1% step increase.', type=float, default=1)
    parser.add_argument(
        '-a', '--amount', help='Amount in USD for each purchase.', type=float, required=True)
    parser.add_argument(
        '-t', '--ticker', help='Ticker of the cryptocurrency. If not provided, BTC will be used.', default='BTC')
    parser.add_argument('-d', '--delay', help='Delay in seconds between each API request.',
                        type=int, default=DEFAULT_API_REQUEST_DELAY)

    args = parser.parse_args()

    ticker_id = get_crypto_ids(args.delay).get(args.ticker.lower())

    if not ticker_id:
        print(f"Cryptocurrency with ticker '{args.ticker}' is not supported.")
        return

    total_crypto, total_investment = calculate_investments(
        args.start, args.end, args.step_percentage, args.amount, args.ticker, ticker_id, args.delay)
    current_price = get_current_price(ticker_id, args.delay)
    price_of_investments = total_crypto * current_price if current_price else None
    delta_percent = ((price_of_investments - total_investment) / total_investment) * 100 if price_of_investments else None

    print(f"\nStarting parameters:")
    print(f"Start Date: {args.start}")
    print(
        f"End Date: {args.end if args.end else 'Today (' + datetime.datetime.now().strftime('%d-%m-%Y') + ')'}")
    print(f"Step Percentage: {args.step_percentage}%")
    print(f"Investment Amount: ${args.amount}")
    print(f"Cryptocurrency Ticker: {args.ticker}\n")
    print(f"Total investment amount: ${total_investment:.2f}")
    print(f"Total amount of {args.ticker}: {total_crypto:.8f}")
    if price_of_investments:
        print(
            f"Price of investments in fiat today: ${price_of_investments:.2f}")
        print(
            f"Delta in percent between invested money and current price of investments: {delta_percent:.2f}%")
    else:
        print("Failed to calculate the current value of investments.")


if __name__ == "__main__":
    main()
