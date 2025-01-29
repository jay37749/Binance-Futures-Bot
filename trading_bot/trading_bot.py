import logging
import time
from binance.client import Client
from strategy import load_trained_model, load_or_train_rl, add_features, trading_strategy
from risk_management import manage_risk, track_open_positions
from data_fetching import get_real_time_data_via_websocket, get_historical_data
from config import Config
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retry decorator for API calls
def retry_on_failure(func, retries=3, backoff=1):
    for attempt in range(retries):
        try:
            return func()
        except RequestException as e:
            logger.warning(f"Retry {attempt + 1}/{retries} for {func.__name__}: {e}")
            time.sleep(backoff * (2 ** attempt))
    logger.error(f"Max retries reached for {func.__name__}.")
    return None

# Apply slippage and fees in live mode
def apply_slippage_and_fees(price, slippage_pct=0.05, fee_pct=0.1):
    slippage = price * slippage_pct / 100
    fee = price * fee_pct / 100
    return price - slippage - fee

def websocket_callback(df, client, pair, higher_timeframe_df, xgboost_model, rl_model, config, open_positions):
    """
    Callback function for WebSocket to process incoming real-time data.
    Executes hybrid trading strategy, risk management, and tracks positions.
    """
    try:
        if df is None or df.empty:
            logger.error(f"No real-time data for {pair}. Skipping.")
            return

        if higher_timeframe_df is None or higher_timeframe_df.empty:
            logger.error(f"No higher timeframe data for {pair}. Skipping.")
            return

        # Add features (indicators) to the real-time data
        df = add_features(df)

        # Apply slippage and fees
        df['close'] = df['close'].apply(apply_slippage_and_fees)

        # Execute hybrid trading strategy
        signal = trading_strategy(df, higher_timeframe_df, xgboost_model, rl_model, mode="hybrid")

        # Extract necessary trade details
        current_price = df['close'].iloc[-1]
        stop_loss, take_profit = manage_risk(client, pair, signal, df, config) or (None, None)

        if stop_loss and take_profit:
            # Track open positions and log profit/loss
            open_positions[pair] = track_open_positions(
                client, pair, open_positions.get(pair), current_price, stop_loss, take_profit
            )
        else:
            logger.info(f"No trade executed for {pair}. Risk parameters unavailable.")

    except Exception as e:
        logger.error(f"Error trading {pair}: {e}", exc_info=True)

def run_bot(live_trading=True):
    config = Config()

    # Initialize Binance client with API credentials
    api_key, api_secret = config.get_api_credentials()
    client = Client(api_key, api_secret)

    trading_pairs = config.get_trading_pairs()

    # Load models
    try:
        xgboost_model = load_trained_model()
        rl_model = load_or_train_rl()
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return

    open_positions = {}  # Dictionary to track open positions for each pair

    if live_trading:
        logger.info("Starting live WebSocket data stream...")

        # Start WebSocket for real-time data fetching
        get_real_time_data_via_websocket(trading_pairs, client, interval='1m', fetch_order_book=True)

        # Pre-fetch higher timeframe data
        higher_timeframe_dfs = {}
        for pair in trading_pairs:
            higher_timeframe_dfs[pair] = retry_on_failure(
                lambda: get_historical_data(client, pair, interval='4h', lookback='3 months ago UTC')
            )

        # Main live trading loop
        while True:
            try:
                for pair in trading_pairs:
                    # Fetch real-time data for the pair
                    df = retry_on_failure(
                        lambda: get_historical_data(client, pair, interval='1m', lookback='1 hour ago UTC')
                    )
                    if df is None or df.empty:
                        logger.warning(f"No real-time data for {pair}. Skipping.")
                        continue

                    # Pass data to the callback for processing
                    websocket_callback(
                        df,
                        client,
                        pair,
                        higher_timeframe_dfs.get(pair),
                        xgboost_model,
                        rl_model,
                        config,
                        open_positions
                    )

            except Exception as e:
                logger.error(f"Error in live trading loop: {e}", exc_info=True)

            # Delay between WebSocket processing cycles
            time.sleep(1)

    else:
        logger.info("Starting backtest mode...")
        for pair in trading_pairs:
            try:
                # Fetch historical data for backtesting
                df = retry_on_failure(
                    lambda: get_historical_data(client, pair, interval='1h', lookback='8 months ago UTC')
                )
                if df is None or df.empty:
                    logger.error(f"No backtest data for {pair}. Skipping.")
                    continue

                # Fetch higher timeframe data
                higher_timeframe_df = retry_on_failure(
                    lambda: get_historical_data(client, pair, interval='4h', lookback='8 months ago UTC')
                )
                if higher_timeframe_df is None or higher_timeframe_df.empty:
                    logger.error(f"No higher timeframe data for {pair}. Skipping.")
                    continue

                # Add features (indicators) to the historical data
                df = add_features(df)

                # Apply slippage and fees
                df['close'] = df['close'].apply(apply_slippage_and_fees)

                # Execute hybrid trading strategy
                signal = trading_strategy(df, higher_timeframe_df, xgboost_model, rl_model, mode="hybrid")

                # Manage risk and execute orders based on the signal
                manage_risk(client, pair, signal, df, config)

            except Exception as e:
                logger.error(f"Error during backtest for {pair}: {e}", exc_info=True)

            # Delay between backtest polling intervals
            time.sleep(config.get_polling_interval())

if __name__ == "__main__":
    logger.info("Starting Binance Futures Trading Bot in live mode...")
    run_bot(live_trading=True)
