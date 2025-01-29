import pandas as pd
import logging

logger = logging.getLogger(__name__)

def analyze_higher_timeframe(df):
    """
    Analyze the higher timeframe data to determine the overall market trend.

    :param df: DataFrame containing higher timeframe data.
    :return: 1 for bullish, -1 for bearish, or None if analysis cannot be performed.
    """
    if df is None or df.empty:
        logger.error("Higher timeframe data is None or empty. Cannot analyze market trend.")
        return None

    if 'close' not in df.columns:
        logger.error("Higher timeframe data is missing 'close' column. Cannot analyze market trend.")
        return None

    # Ensure there are enough data points for rolling calculations
    if len(df) < 200:
        logger.warning("Insufficient data for moving average calculations. Returning neutral trend.")
        return 0  # Neutral

    df = df.copy()  # Avoid modifying the original DataFrame
    df['short_ma'] = df['close'].rolling(window=50).mean()
    df['long_ma'] = df['close'].rolling(window=200).mean()

    if df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1]:
        return 1  # Bullish
    elif df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1]:
        return -1  # Bearish
    else:
        return 0  # Neutral (no clear trend)

def detect_market_environment(df):
    """
    Detect the current market environment based on ADX and volatility.

    :param df: DataFrame containing market data with 'adx', 'atr', and 'close' columns.
    :return: String indicating the market environment ('trending', 'ranging', 'volatile', 'low_volatility') or None.
    """
    if df is None or df.empty:
        logger.error("DataFrame is None or empty. Cannot detect market environment.")
        return None

    required_columns = ['adx', 'atr', 'close']
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Missing required column '{col}' in DataFrame. Cannot detect market environment.")
            return None

    try:
        adx_value = df['adx'].iloc[-1]
        volatility = df['atr'].iloc[-1] / df['close'].iloc[-1]

        if adx_value > 25 and volatility > 0.02:
            return 'trending'
        elif adx_value < 20 and volatility < 0.01:
            return 'ranging'
        elif volatility > 0.03:
            return 'volatile'
        else:
            return 'low_volatility'
    except Exception as e:
        logger.error(f"Error while detecting market environment: {e}")
        return None