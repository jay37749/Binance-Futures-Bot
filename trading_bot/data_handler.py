import pandas as pd
import numpy as np
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

# Function to calculate ATR (Average True Range)
def calculate_atr(df, window=14):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot calculate ATR.")
        df['atr'] = np.nan
        return df

    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    df['atr'] = true_range.rolling(window=window).mean()
    return df

# Function to calculate ADX (Average Directional Index)
def calculate_adx(df, window=14):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot calculate ADX.")
        df['adx'] = np.nan
        return df

    df['tr'] = np.maximum(
        df['high'] - df['low'], 
        np.maximum(np.abs(df['high'] - df['close'].shift()), np.abs(df['low'] - df['close'].shift()))
    )
    df['dm_plus'] = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']),
                             np.maximum(df['high'] - df['high'].shift(), 0), 0)
    df['dm_minus'] = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()),
                              np.maximum(df['low'].shift() - df['low'], 0), 0)

    df['tr_smooth'] = df['tr'].rolling(window=window).sum()
    df['dm_plus_smooth'] = df['dm_plus'].rolling(window=window).sum()
    df['dm_minus_smooth'] = df['dm_minus'].rolling(window=window).sum()

    df['di_plus'] = 100 * (df['dm_plus_smooth'] / df['tr_smooth'])
    df['di_minus'] = 100 * (df['dm_minus_smooth'] / df['tr_smooth'])
    df['dx'] = 100 * (np.abs(df['di_plus'] - df['di_minus']) / (df['di_plus'] + df['di_minus']))

    df['adx'] = df['dx'].rolling(window=window).mean()
    df.drop(columns=['tr', 'dm_plus', 'dm_minus', 'tr_smooth', 'dm_plus_smooth', 'dm_minus_smooth', 'di_plus', 'di_minus', 'dx'], inplace=True)
    return df

# Function to detect market environment
def detect_market_environment(row):
    """
    Determines the market environment based on technical indicators.

    :param row: Pandas Series with the necessary technical indicators.
    :return: A string representing the market environment ('trending', 'ranging', 'volatile', or 'low_volatility').
    """
    try:
        adx = row.get('adx', np.nan)
        atr = row.get('atr', np.nan)
        close = row.get('close', np.nan)

        if pd.isna(adx) or pd.isna(atr) or pd.isna(close):
            logger.warning("Missing data for market environment detection. Returning 'unknown'.")
            return 'unknown'

        if adx > 25 and atr / close > 0.02:
            return 'trending'
        elif adx < 20 and atr / close < 0.01:
            return 'ranging'
        elif atr / close > 0.03:
            return 'volatile'
        else:
            return 'low_volatility'
    except Exception as e:
        logger.error(f"Error in detecting market environment: {e}")
        return 'unknown'

# Function to calculate On-Balance Volume (OBV)
def calculate_obv(df):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot calculate OBV.")
        df['obv'] = np.nan
        return df

    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    return df

# Function to calculate VWAP (Volume Weighted Average Price)
def calculate_vwap(df):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot calculate VWAP.")
        df['vwap'] = np.nan
        return df

    df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    return df

# Function to calculate Ichimoku Cloud
def calculate_ichimoku(df):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot calculate Ichimoku Cloud.")
        return df

    nine_period_high = df['high'].rolling(window=9).max()
    nine_period_low = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (nine_period_high + nine_period_low) / 2

    twenty_six_period_high = df['high'].rolling(window=26).max()
    twenty_six_period_low = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (twenty_six_period_high + twenty_six_period_low) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    fifty_two_period_high = df['high'].rolling(window=52).max()
    fifty_two_period_low = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((fifty_two_period_high + fifty_two_period_low) / 2).shift(26)
    df['chikou_span'] = df['close'].shift(-26)
    return df

# Function to calculate Returns
def calculate_returns(df):
    df = df.copy()  # Work with a copy of the DataFrame
    df.loc[:, 'returns'] = df['close'].pct_change().fillna(0)
    return df

# Function to calculate Volatility
def calculate_volatility(df, window=21):
    df = calculate_returns(df)
    df = df.copy()
    df.loc[:, 'volatility'] = df['returns'].rolling(window=window).std()
    return df

# Function to calculate Momentum
def calculate_momentum(df, window=21):
    df['momentum'] = df['close'].diff(window).fillna(0)
    return df

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(df, window=20):
    rolling_mean = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std()
    df['bb_upper'] = rolling_mean + (rolling_std * 2)
    df['bb_lower'] = rolling_mean - (rolling_std * 2)
    return df

# Function to calculate MACD
def calculate_macd(df):
    short_ema = df['close'].ewm(span=12, adjust=False).mean()
    long_ema = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = short_ema - long_ema
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']
    return df

# Function to calculate RSI
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# Function to calculate Stochastic Oscillator
def calculate_stochastic(df, k_window=14, d_window=3):
    low_min = df['low'].rolling(window=k_window).min()
    high_max = df['high'].rolling(window=k_window).max()
    df['stochastic_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)
    df['stochastic_d'] = df['stochastic_k'].rolling(window=d_window).mean()
    return df

# Function to calculate Moving Averages
def calculate_moving_averages(df, short_window=50, long_window=200):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    return df

# Function to fetch sentiment data
def fetch_sentiment_data(df):
    if 'news' not in df.columns or df['news'].isnull().all():
        logger.warning("No news data available for sentiment analysis.")
        df['sentiment'] = np.nan
        return df

    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['news'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])
    return df


# Function to calculate confluence signals
def confluence_signals(row, higher_timeframe_trend):
    """
    Calculates the confluence of buy and sell signals based on technical indicators and market environment.
    """
    buy_confluence = 0
    sell_confluence = 0

    if row['short_ma'] > row['long_ma']:
        buy_confluence += 1
    if row['short_ma'] < row['long_ma']:
        sell_confluence += 1
    if row['macd_diff'] > 0:
        buy_confluence += 1
    if row['macd_diff'] < 0:
        sell_confluence += 1
    if row['rsi'] < 30:
        buy_confluence += 1
    if row['rsi'] > 70:
        sell_confluence += 1

    if higher_timeframe_trend == 1:
        buy_confluence += 1
    elif higher_timeframe_trend == -1:
        sell_confluence += 1

    return buy_confluence, sell_confluence

# Function to add features
def add_features(df):
    if df is None or df.empty:
        logger.warning("DataFrame is empty. Cannot add features.")
        return df

    df = calculate_returns(df)
    df = calculate_volatility(df)
    df = calculate_momentum(df)
    df = calculate_atr(df)
    df = calculate_adx(df)
    df = calculate_obv(df)
    df = calculate_vwap(df)
    df = calculate_ichimoku(df)
    df = calculate_bollinger_bands(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df = calculate_stochastic(df)
    df = calculate_moving_averages(df)

    if 'news' in df.columns:
        df = fetch_sentiment_data(df)

    return df
