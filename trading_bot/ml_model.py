import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange

def train_model(data):
    data = preprocess_data(data)
    X = data[['close', 'rsi', 'ema', 'atr']]
    y = data['signal']
    model = RandomForestClassifier()
    model.fit(X, y)
    joblib.dump(model, 'model.pkl')

def predict_signal(data):
    data = preprocess_data(data)
    model = joblib.load('model.pkl')
    X = data[['close', 'rsi', 'ema', 'atr']]
    return model.predict(X)

def preprocess_data(data):
    data['rsi'] = RSIIndicator(data['close']).rsi()
    data['ema'] = EMAIndicator(data['close']).ema_indicator()
    data['atr'] = AverageTrueRange(data['high'], data['low'], data['close']).average_true_range()
    return data
