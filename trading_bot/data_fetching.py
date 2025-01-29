import logging
import pandas as pd
import time
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance import ThreadedWebsocketManager
from error_handler import handle_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exponential backoff for retry mechanism
def retry_api_call(func, *args, retries=5, delay=2, **kwargs):
    attempts = 0
    while attempts < retries:
        try:
            return func(*args, **kwargs)
        except BinanceAPIException as e:
            handle_error(e, error_type="API", critical=False)
        except Exception as e:
            handle_error(e, error_type="General", critical=False)
        attempts += 1
        time.sleep(delay ** attempts)
    logger.error(f"Failed to execute {func.__name__} after {retries} retries.")
    return None

# WebSocket integration for real-time data fetching
def start_websocket(client, symbols, interval='1m', fetch_order_book=False, rate_limit=5, batch_size=2):
    """
    Initialize a Binance WebSocket manager to fetch real-time data for given symbols.

    :param client: Binance Client object
    :param symbols: List of trading pairs to subscribe to (e.g., ['BTCUSDT'])
    :param interval: Time interval for candlestick data (default: '1m')
    :param fetch_order_book: Boolean indicating whether to fetch real-time order book data
    :param rate_limit: Maximum number of updates per second to throttle real-time updates.
    :param batch_size: Number of symbols to process simultaneously in each batch.
    """
    def process_message(msg):
        """
        Callback function to process incoming WebSocket messages.
        """
        if msg['e'] == 'error':
            handle_error(msg, error_type="WebSocket", critical=False)
        else:
            try:
                symbol = msg['s']
                kline = msg['k']
                df = pd.DataFrame([[
                    kline['t'], kline['o'], kline['h'], kline['l'], kline['c'], kline['v']
                ]], columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)

                logger.info(f"Real-time update for {symbol}: {df.tail(1)}")

                if fetch_order_book:
                    order_book = get_order_book(client, symbol)
                    logger.info(f"Order book for {symbol}: {order_book}")
            except Exception as e:
                handle_error(e, error_type="WebSocket Processing", critical=False)

    twm = ThreadedWebsocketManager(api_key=client.API_KEY, api_secret=client.API_SECRET)
    twm.start()

    def subscribe_batch(batch):
        for symbol in batch:
            logger.info(f"Subscribing to WebSocket for {symbol} with interval {interval}")
            twm.start_kline_socket(callback=process_message, symbol=symbol, interval=interval)
            time.sleep(1 / rate_limit)  # Throttle subscriptions to respect rate limits

    # Process symbols in batches
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        subscribe_batch(batch)

    logger.info(f"WebSocket initiated for {symbols} at {interval} interval.")

# Fetch order book data
def get_order_book(client, symbol, limit=10):
    try:
        order_book = retry_api_call(client.get_order_book, symbol=symbol, limit=limit)
        if order_book:
            return {
                'bids': order_book['bids'][:limit],
                'asks': order_book['asks'][:limit]
            }
        logger.error(f"Empty order book data for {symbol}.")
    except Exception as e:
        handle_error(e, error_type="Order Book", critical=False)
    return {}

# Fetch Crypto Fear & Greed Index
def get_crypto_fear_greed_index():
    """
    Fetch the Crypto Fear & Greed Index from an external API.

    :return: Current Fear & Greed Index value (0-100) or None if unavailable.
    """
    url = "https://api.alternative.me/fng/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return int(data['data'][0]['value'])
    except Exception as e:
        handle_error(e, error_type="Sentiment API", critical=False)
    return None

# Fetch real-time data via WebSocket
def get_real_time_data_via_websocket(symbols, client, interval='1m', fetch_order_book=False):
    """
    Initializes the WebSocket and listens for real-time updates for the given symbols.

    :param symbols: List of trading symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
    :param client: Binance client object.
    :param interval: Candlestick interval for the WebSocket stream (default: '1m')
    :param fetch_order_book: Boolean to indicate fetching order book data.
    """
    logger.info(f"Starting WebSocket data stream for symbols: {symbols} at interval: {interval}")
    start_websocket(client, symbols, interval, fetch_order_book=fetch_order_book)

# Fetch historical data for backtesting
def get_historical_data(client, symbol, interval='1h', lookback='84 months ago UTC'):
    """
    Fetch historical candlestick data for the given trading pair and interval.

    :param client: Binance client object.
    :param symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT').
    :param interval: Time interval (e.g., '1h', '1d').
    :param lookback: Time range for historical data (e.g., '1 month ago UTC').
    :return: Pandas DataFrame with historical data.
    """
    try:
        klines = retry_api_call(client.get_historical_klines, symbol, interval, lookback)
        if klines:
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df.set_index('open_time', inplace=True)

            for col in ['open', 'close', 'high', 'low', 'volume']:
                df[col] = df[col].astype(float)

            if df.empty or df.isnull().values.any():
                logger.error(f"Historical data contains empty or NaN values for {symbol}.")
                return pd.DataFrame()
            logger.info(f"Fetched historical data for {symbol}: {df.shape[0]} rows.")
            return df[['open', 'high', 'low', 'close', 'volume']]
        logger.error(f"Empty historical data response for {symbol}.")
    except BinanceAPIException as e:
        handle_error(e, error_type="Historical Data API", critical=False)
    except Exception as e:
        handle_error(e, error_type="Historical Data", critical=False)
    return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    client = Client('your_api_key', 'your_api_secret')
    symbols = ['BTCUSDT', 'ETHUSDT']

    # Fetch Crypto Fear & Greed Index
    fear_greed_index = get_crypto_fear_greed_index()
    if fear_greed_index is not None:
        logger.info(f"Current Crypto Fear & Greed Index: {fear_greed_index}")

    # Start WebSocket for real-time data fetching with order book
    get_real_time_data_via_websocket(symbols, client, interval='1m', fetch_order_book=True)