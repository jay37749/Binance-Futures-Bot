import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import logging
import joblib
from binance.client import Client
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gym
from data_handler import add_features, confluence_signals
from data_fetching import get_historical_data
import os

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
ACCURACY_THRESHOLD = 0.75
MAX_TRAINING_ATTEMPTS = 8
XGB_MODEL_FILE = 'trained_xgboost_model.pkl'
RL_MODEL_FILE = 'trained_rl_model.zip'
FEATURE_COLUMNS = ['returns', 'volatility', 'momentum', 'bb_upper', 'bb_lower', 'macd_diff', 'rsi', 'adx', 'short_ma', 'long_ma']
EXPECTED_RL_INPUT_SIZE = 28  # Expected size for RL model input

# Multi-Timeframe Analysis
def analyze_higher_timeframe(df):
    if df is None or df.empty or 'close' not in df.columns:
        logger.error("Higher timeframe data is invalid.")
        return None
    df['short_ma'] = df['close'].rolling(window=50).mean()
    df['long_ma'] = df['close'].rolling(window=200).mean()
    return 1 if df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1] else -1

# Load and Train Models
def train_and_save_best_model():
    xgboost_model = load_trained_model("xgboost")
    rl_model = load_or_train_rl()
    return xgboost_model, rl_model

def load_or_train_rl():
    if os.path.exists(RL_MODEL_FILE):
        try:
            model = PPO.load(RL_MODEL_FILE)
            logger.info("Pre-trained RL model loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Error loading RL model: {e}. Training a new model.")
    logger.warning("RL model not found. Training a new model.")
    return train_rl_model()

def load_trained_model(model_type="xgboost"):
    if model_type == "xgboost":
        try:
            model = joblib.load(XGB_MODEL_FILE)
            logger.info("Pre-trained XGBoost model loaded successfully.")
            return model
        except FileNotFoundError:
            logger.error("XGBoost model not found. Retraining required.")
            return train_and_save_xgboost()
    raise ValueError(f"Invalid model_type: {model_type}. Must be 'xgboost' or 'rl'.")

def train_and_save_xgboost():
    df = get_historical_data(Client('your_api_key', 'your_api_secret'), 'BTCUSDT', '1h', '84 months ago UTC')
    if df is None or df.empty:
        logger.error("No data available to train the XGBoost model.")
        return None
    df = add_features(df)
    df['target'] = df.apply(label_action, axis=1).dropna()
    X = df[FEATURE_COLUMNS]
    y = df['target'].map({-1: 0, 0: 1, 1: 2})
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    best_model, best_accuracy = None, 0.0
    for attempt in range(MAX_TRAINING_ATTEMPTS):
        model = XGBClassifier(random_state=42)
        model.fit(X_train, y_train)
        accuracy = accuracy_score(y_test, model.predict(X_test))
        if accuracy > best_accuracy:
            best_model, best_accuracy = model, accuracy
        if accuracy >= ACCURACY_THRESHOLD:
            break
    if best_model:
        joblib.dump(best_model, XGB_MODEL_FILE)
    return best_model

def train_rl_model():
    df = get_historical_data(Client('your_api_key', 'your_api_secret'), 'BTCUSDT', '1h', '84 months ago UTC')
    if df is None or df.empty:
        logger.error("No data available to train the RL model.")
        return None
    df = add_features(df).dropna()
    env = TradingEnvironment(df)
    model = PPO('MlpPolicy', DummyVecEnv([lambda: env]), verbose=1)
    model.learn(total_timesteps=50000)
    model.save(RL_MODEL_FILE)
    return model

# Hybrid Decision-Making
def trading_strategy(df, higher_timeframe_df, xgboost_model, rl_model, mode="hybrid"):
    higher_timeframe_trend = analyze_higher_timeframe(higher_timeframe_df)
    df = add_features(df)
    if df.empty:
        logger.error("DataFrame is empty after adding features. Returning 'HOLD'.")
        return 'HOLD'
    if not set(FEATURE_COLUMNS).issubset(df.columns):
        logger.error("DataFrame missing required features for prediction.")
        return 'HOLD'
    xgboost_signal = xgboost_model.predict(df.iloc[-1:][FEATURE_COLUMNS])[0]
    xgboost_signal = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}.get(xgboost_signal, 'HOLD')
    if mode == "xgboost-only":
        return xgboost_signal
    base_rl_input = df.iloc[-1:][FEATURE_COLUMNS].values.flatten()
    if mode == "rl-only":
        rl_input = base_rl_input
    elif mode == "hybrid":
        buy_conf, sell_conf = confluence_signals(df.iloc[-1], higher_timeframe_trend)
        rl_input = np.concatenate((np.array([1 if xgboost_signal == 'BUY' else -1 if xgboost_signal == 'SELL' else 0, buy_conf, sell_conf, higher_timeframe_trend]), base_rl_input))
    rl_input = np.pad(rl_input, (0, EXPECTED_RL_INPUT_SIZE - len(rl_input)), mode='constant')[:EXPECTED_RL_INPUT_SIZE]
    if not np.isfinite(rl_input).all():
        logger.error(f"Invalid rl_input detected: {rl_input}")
        rl_input = np.nan_to_num(rl_input)
        logger.info(f"Cleaned rl_input: {rl_input}")
    rl_signal = rl_model.predict(rl_input.reshape(1, -1))[0]
    rl_signal = rl_signal.item() if isinstance(rl_signal, np.ndarray) else rl_signal
    return {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}.get(rl_signal, 'HOLD')

# Custom RL Environment
class TradingEnvironment(gym.Env):
    def __init__(self, data):
        super().__init__()
        self.data = self.clean_data(data)
        self.current_step = 0
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(28,), dtype=np.float32)
        self.balance = 100.0
        self.position = 0.0

    def clean_data(self, data):
        return data.replace({np.nan: 0}).applymap(lambda x: 0 if isinstance(x, str) else x)

    def reset(self):
        self.current_step = 0
        self.balance = 100.0
        self.position = 0.0
        return self._get_observation()

    def _get_observation(self):
        row = self.data.iloc[self.current_step].values[:26].astype(np.float32)
        obs = np.concatenate([row, [self.balance, self.position]])
        return obs

    def step(self, action):
        reward = 0
        done = False
        if action == 2:
            self.position = self.balance / self.data.iloc[self.current_step]['close']
            self.balance = 0
        elif action == 0:
            self.balance = self.position * self.data.iloc[self.current_step]['close']
            reward = self.balance - 100.0
            self.position = 0
        self.current_step += 1
        if self.current_step >= len(self.data) - 1:
            done = True
        return self._get_observation(), reward, done, {}

# Label Actions
def label_action(row):
    buy_conf, sell_conf = confluence_signals(row, higher_timeframe_trend=None)
    return 1 if buy_conf > sell_conf else -1 if sell_conf > buy_conf else 0
