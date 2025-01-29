# run_bot.py

import sys
import logging
from trading_bot import run_bot
from backtest import run_backtest
from strategy import load_trained_model, train_and_save_best_model, load_or_train_rl
from data_fetching import get_historical_data
from config import Config
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to retrain XGBoost periodically
def periodic_xgboost_retraining(interval_hours=24):
    """
    Periodically retrain the XGBoost model with the latest trade data.
    :param interval_hours: Number of hours between retraining cycles.
    """
    logger.info(f"Starting periodic XGBoost retraining every {interval_hours} hours...")
    config = Config()
    api_key, api_secret = config.get_api_credentials()
    client = Client(api_key, api_secret)

    while True:
        try:
            # Fetch recent data for retraining
            trading_pairs = config.get_trading_pairs()
            for pair in trading_pairs:
                logger.info(f"Fetching recent data for {pair}...")
                df = get_historical_data(client, pair, '1h', '2 months ago UTC')  # Adjust lookback as needed
                if df is None or df.empty:
                    logger.warning(f"No data available for {pair}. Skipping retraining for this pair.")
                    continue
                
                # Retrain the model
                logger.info(f"Retraining XGBoost model for {pair}...")
                train_and_save_best_model()

            logger.info(f"XGBoost retraining completed. Next retraining in {interval_hours} hours.")
            time.sleep(interval_hours * 3600)

        except Exception as e:
            logger.error(f"Error during XGBoost retraining: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

# Function to enable live RL learning
def live_rl_learning():
    """
    Perform live RL decision-making and learning.
    """
    logger.info("Initializing live RL decision-making and learning...")
    rl_model = load_or_train_rl()
    config = Config()
    api_key, api_secret = config.get_api_credentials()
    client = Client(api_key, api_secret)
    trading_pairs = config.get_trading_pairs()

    while True:
        try:
            for pair in trading_pairs:
                logger.info(f"Fetching real-time data for {pair}...")
                df = get_historical_data(client, pair, '1m', '1 day ago UTC')  # Real-time minute-level data
                if df is None or df.empty:
                    logger.warning(f"No real-time data available for {pair}. Skipping RL decision-making.")
                    continue

                # Prepare the state for RL decision-making
                current_price = float(client.futures_symbol_ticker(symbol=pair)['price'])
                state = {
                    'data': df,
                    'current_price': current_price,
                }

                # Perform RL prediction
                logger.info(f"Performing RL decision-making for {pair}...")
                rl_action = rl_model.predict([state], deterministic=True)[0]

                # Log the RL action
                action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
                logger.info(f"RL Action for {pair}: {action_map.get(rl_action, 'UNKNOWN')}")

                # Implement live actions (e.g., placing trades)
                if action_map.get(rl_action) in ["BUY", "SELL"]:
                    logger.info(f"Executing {action_map[rl_action]} trade for {pair}...")

            time.sleep(60)  # Wait 1 minute before the next RL decision cycle

        except Exception as e:
            logger.error(f"Error during live RL learning: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

def main():
    # Check if the mode argument is passed
    if len(sys.argv) < 2:
        logger.error("No mode provided. Usage: python run_bot.py --mode [live|backtest|train_rl|retrain_xgboost]")
        return

    # Parse the mode argument
    mode_arg = sys.argv[1].lower()

    if mode_arg == '--mode=live':
        logger.info("Starting Binance Futures Trading Bot in live mode...")
        run_bot(live_trading=True)
    elif mode_arg == '--mode=backtest':
        logger.info("Starting backtest mode...")
        run_backtest()
    elif mode_arg == '--mode=train_rl':
        logger.info("Starting live RL learning mode...")
        live_rl_learning()
    elif mode_arg == '--mode=retrain_xgboost':
        logger.info("Starting periodic XGBoost retraining mode...")
        periodic_xgboost_retraining()
    else:
        logger.error("Invalid mode. Use '--mode=live', '--mode=backtest', '--mode=train_rl', or '--mode=retrain_xgboost'.")

if __name__ == "__main__":
    main()
