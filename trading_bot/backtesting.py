import pandas as pd
from ml_model import preprocess_data, predict_signal

def backtest_strategy(data):
    data = preprocess_data(data)
    data['signal'] = predict_signal(data)

    initial_balance = 10000
    balance = initial_balance
    position = 0

    for i in range(1, len(data)):
        if data['signal'][i] == 1 and position == 0:
            position = balance / data['close'][i]
            balance -= position * data['close'][i]
        elif data['signal'][i] == -1 and position > 0:
            balance += position * data['close'][i]
            position = 0

    final_balance = balance + position * data['close'][-1]
    return final_balance

# Example usage
# data = pd.read_csv('historical_data.csv')
# final_balance = backtest_strategy(data)
# print(f"Final balance: {final_balance}")

