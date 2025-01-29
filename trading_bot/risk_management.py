import logging
import time
from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException
from utils import detect_market_environment
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

open_positions = {}

def calculate_atr(df, window=14):
    if df.empty or 'high' not in df or 'low' not in df or 'close' not in df:
        logger.error("DataFrame is empty or missing required columns for ATR calculation.")
        return None
    df['tr'] = df.apply(lambda row: max(row['high'] - row['low'], abs(row['high'] - row['close']), abs(row['low'] - row['close'])), axis=1)
    return df['tr'].rolling(window=window).mean().iloc[-1]

def get_futures_balance(client):
    try:
        account_info = client.futures_account()
        return float(account_info['totalWalletBalance'])
    except BinanceAPIException as e:
        logger.error(f"Error fetching futures balance: {e}")
        return 0

def calculate_position_size(balance, atr, risk_percentage=0.01):
    if atr <= 0:
        logger.error("ATR is non-positive. Cannot calculate position size.")
        return 0
    return max(0, (balance * risk_percentage) / atr)

def calculate_stop_loss_take_profit(current_price, atr, risk_factor=2, reward_factor=6):
    if atr <= 0:
        logger.error("ATR is non-positive. Cannot calculate stop-loss and take-profit.")
        return None, None
    return max(0, current_price - atr * risk_factor), max(0, current_price + atr * reward_factor)

def manage_risk(client, symbol, signal, df, config, max_retries=3, retry_delay=2):
    """
    Manages trading risk by calculating position size, stop-loss, and take-profit levels,
    and placing trades if the risk-to-reward ratio is acceptable.
    """
    try:
        # Validate signal
        if signal not in ["BUY", "SELL"]:
            logger.error(f"Invalid trading signal '{signal}' for {symbol}. Skipping trade.")
            return

        # Log the market environment
        market_environment = detect_market_environment(df)
        logger.info(f"Market environment for {symbol}: {market_environment}")

        # Retry fetching current price and balance
        current_price = None
        futures_balance = None
        for attempt in range(max_retries):
            try:
                current_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
                futures_balance = get_futures_balance(client)
                break
            except BinanceAPIException as e:
                logger.error(f"BinanceAPIException while fetching data for {symbol}: {e}")
                logger.warning(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
        else:
            logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts. Skipping trade.")
            return

        # Calculate ATR and position size
        atr = calculate_atr(df)
        if atr is None:
            logger.warning(f"ATR could not be calculated for {symbol}. Skipping trade.")
            return
        position_size = calculate_position_size(futures_balance, atr, config.get_risk_percentage())

        # Calculate stop-loss and take-profit
        stop_loss, take_profit = calculate_stop_loss_take_profit(
            current_price, atr, config.get_risk_factor(), config.get_reward_factor()
        )
        if stop_loss is None or take_profit is None:
            logger.warning(f"Stop-loss or take-profit could not be calculated for {symbol}. Skipping trade.")
            return

        # Log calculated risk parameters
        logger.info(f"Risk parameters for {symbol}:")
        logger.info(f"  Current price: {current_price}")
        logger.info(f"  ATR: {atr}")
        logger.info(f"  Position size: {position_size}")
        logger.info(f"  Stop-loss: {stop_loss}")
        logger.info(f"  Take-profit: {take_profit}")

        # Check the risk-to-reward ratio
        risk_to_reward_ratio = (take_profit - current_price) / (current_price - stop_loss)
        if risk_to_reward_ratio >= config.get_min_risk_to_reward():
            # Place trade
            side = SIDE_BUY if signal == "BUY" else SIDE_SELL
            place_futures_order(client, symbol, side, position_size, config.get_leverage(symbol), stop_loss, take_profit)
            track_open_positions(symbol, signal, position_size, current_price, stop_loss, take_profit)
        else:
            logger.info(f"Trade skipped for {symbol} due to suboptimal risk-to-reward ratio: {risk_to_reward_ratio:.2f}")

    except BinanceAPIException as e:
        logger.error(f"BinanceAPIException in manage_risk for {symbol}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in manage_risk for {symbol}: {e}")

def track_open_positions(symbol, side, quantity, entry_price, stop_loss, take_profit):
    open_positions[symbol] = {
        "side": side,
        "quantity": quantity,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
    }
    logger.info(f"Position tracked for {symbol}: {open_positions[symbol]}")

def place_futures_order(client, symbol, side, quantity, leverage, stop_loss=None, take_profit=None):
    try:
        # Validate the side parameter
        if side not in [SIDE_BUY, SIDE_SELL]:
            raise ValueError(f"Invalid side parameter '{side}' for {symbol}. Must be 'BUY' or 'SELL'.")

        # Set leverage and place order
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        order = client.futures_create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)
        logger.info(f"Market order placed: {side} {quantity} of {symbol}")

        # Set stop-loss and take-profit
        if stop_loss and take_profit:
            client.futures_create_order(
                symbol=symbol, side=SIDE_SELL if side == SIDE_BUY else SIDE_BUY, type="STOP_MARKET", stopPrice=stop_loss
            )
            client.futures_create_order(
                symbol=symbol, side=SIDE_SELL if side == SIDE_BUY else SIDE_BUY, type="TAKE_PROFIT_MARKET", stopPrice=take_profit
            )
            logger.info(f"Stop-loss set at {stop_loss}, Take-profit set at {take_profit}")

        return order

    except BinanceAPIException as e:
        logger.error(f"BinanceAPIException in place_futures_order: {e}")
    except ValueError as e:
        logger.error(f"ValueError in place_futures_order: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in place_futures_order: {e}")
    return None
