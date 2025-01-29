import logging
import pandas as pd
import numpy as np
from strategy import load_trained_model, trading_strategy, load_or_train_rl
from risk_management import calculate_stop_loss_take_profit
from data_fetching import get_historical_data
from config import Config
from binance.client import Client
from stable_baselines3 import PPO
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to calculate Sharpe Ratio
def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    mean_return = np.mean(returns)
    std_dev = np.std(returns)
    if std_dev == 0:
        return 0
    return (mean_return - risk_free_rate) / std_dev

# Function to calculate maximum drawdown
def calculate_max_drawdown(equity_curve):
    drawdowns = equity_curve / equity_curve.cummax() - 1
    return drawdowns.min()

# Function to visualize equity curve
def plot_equity_curve(equity_curve, title="Equity Curve"):
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve, label='Equity Curve', color='blue')
    plt.title(title)
    plt.xlabel('Trades')
    plt.ylabel('Equity')
    plt.legend()
    plt.grid()
    plt.show()

# Backtesting logic for a single pair
def backtest_pair(df, xgboost_model, rl_model, pair, leverage=1, higher_timeframe_df=None):
    logger.info(f"Starting backtest for {pair} with leverage {leverage}...")
    initial_balance = 100
    balance = initial_balance
    position_size = 0
    equity_curve = [initial_balance]
    rewards = []

    for i in range(1, len(df)):
        current_row = df.iloc[i]
        df_with_features = df.iloc[:i+1]

        if df_with_features.empty:
            logger.error(f"DataFrame is empty after adding features at row {i}. Skipping this row.")
            continue

        # Generate trading signal
        signal = trading_strategy(df_with_features, higher_timeframe_df, xgboost_model, rl_model, mode="hybrid")
        current_price = current_row['close']

        if signal == 'BUY' and balance > 0:
            position_size = (balance * leverage) / current_price
            balance = 0
            logger.info(f"BUY signal: Bought {pair} at {current_price}")

        elif signal == 'SELL' and position_size > 0:
            balance = position_size * current_price
            rewards.append(balance - initial_balance)  # Reward = Profit/Loss
            position_size = 0
            logger.info(f"SELL signal: Sold {pair} at {current_price}")

        # Update equity curve
        equity = balance + (position_size * current_price)
        equity_curve.append(equity)

    final_balance = balance + position_size * df.iloc[-1]['close']
    profit_loss = final_balance - initial_balance
    logger.info(f"Backtest completed for {pair}. Initial balance: {initial_balance}, Final balance: {final_balance}")

    # Train RL model on rewards
    if rewards:
        rl_model.learn(total_timesteps=len(rewards))

    return {
        'pair': pair,
        'initial_balance': initial_balance,
        'final_balance': final_balance,
        'profit_loss': profit_loss,
        'sharpe_ratio': calculate_sharpe_ratio(pd.Series(equity_curve).pct_change().dropna()),
        'max_drawdown': calculate_max_drawdown(pd.Series(equity_curve)),
        'equity_curve': equity_curve
    }

# Main backtesting function
def run_backtest():
    config = Config()
    trading_pairs = config.get_trading_pairs()

    api_key, api_secret = config.get_api_credentials()
    client = Client(api_key, api_secret)

    xgboost_model = load_trained_model()
    rl_model = load_or_train_rl()

    all_results = []

    for pair in trading_pairs:
        df = get_historical_data(client, pair, '1h', '6 months ago UTC')
        if df is None or df.empty:
            logger.error(f"No data for {pair}. Skipping.")
            continue

        # Fetch higher timeframe data for multi-timeframe analysis
        higher_timeframe_df = get_historical_data(client, pair, interval='4h', lookback='6 months ago UTC')

        # Ensure sufficient data for features and indicators
        if len(df) < 22:  # Example threshold
            logger.error(f"Not enough data for {pair} to calculate features. Skipping this pair.")
            continue

        leverage = config.get_leverage_settings(pair)
        results = backtest_pair(df, xgboost_model, rl_model, pair, leverage, higher_timeframe_df=higher_timeframe_df)
        logger.info(f"Backtest results for {pair}: {results}")

        # Append results for later analysis
        all_results.append(results)

        # Plot equity curve
        plot_equity_curve(results['equity_curve'], title=f"Equity Curve for {pair}")

    # Aggregate results for summary
    summary_df = pd.DataFrame(all_results)
    logger.info("Backtesting Summary:")
    logger.info(summary_df)

if __name__ == "__main__":
    run_backtest()