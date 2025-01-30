<h1 align="center">Hi 👋, I'm jay37749</h1>
<h3 align="center">I'm a professional Frontend Developer from Kenya.</h3>

<p align="left"> <img src="https://komarev.com/ghpvc/?username=jay37749&label=Profile%20views&color=0e75b6&style=flat" alt="jay37749" /> </p>

<p align="left"> <a href="https://github.com/ryo-ma/github-profile-trophy"><img src="https://github-profile-trophy.vercel.app/?username=jay37749" alt="jay37749" /></a> </p>

- 🔭 I’m currently working on [Ultimate Crypto Trading Bot](https://github.com/jay37749/Ultimate-Crypto-Trading-Bot.git)

- 👯 I’m looking to collaborate on [Ulitimate Crypto Trading Bot](https://github.com/jay37749/Ultimate-Crypto-Trading-Bot.git)

- 🤝 I’m looking for help with [Ulitimate Crypto Trading Bot](https://github.com/jay37749/Ultimate-Crypto-Trading-Bot.git)

- 📫 How to reach me **jay37749@gmail.com**
- Welcome to the Ultimate Crypto Trading Bot! This bot is designed to automate cryptocurrency trading using a hybrid strategy that combines XGBoost (machine learning) and PPO (reinforcement learning). It supports live trading, backtesting, and periodic retraining of models. Below, you'll find everything you need to set up, configure, and run the bot.

**Table of Contents**

*Overview*

Prerequisites

*Installation*

*Configuration*

*Running the Bot*

*Live Trading Mode*

*Backtesting Mode*

*Retrain XGBoost Model*

*Live RL Learning Mode*

*Risk Management*

*Troubleshooting*

*Contributing*

*License*

**Overview**

The bot is built to trade on Binance Futures and uses the following key components:

XGBoost Model: A machine learning model trained to predict buy/sell signals.

PPO Model: A reinforcement learning model that adapts to market conditions.

Hybrid Strategy: Combines signals from both XGBoost and PPO for decision-making.

Risk Management: Implements stop-loss, take-profit, and position sizing.

Backtesting: Evaluates the strategy on historical data.

Real-Time Trading: Executes trades in real-time using WebSocket.


**Prerequisites**

Before running the bot, ensure you have the following installed:

Python 3.8 or higher

Binance API Key and Secret: Obtain these from your Binance account.

Required Python Libraries:

pandas

numpy

binance

xgboost

stable-baselines3

scikit-learn

matplotlib

vaderSentiment

You can install the required libraries using the following command:

Copy

pip install pandas numpy binance xgboost stable-baselines3 scikit-learn matplotlib vaderSentiment


Installation

Clone the Repository:

Copy

git clone https://github.com/your-repo/ultimate-crypto-trading-bot.git
cd ultimate-crypto-trading-bot


Set Up Configuration:

Open the config.json file and replace the api_key and api_secret with your Binance API credentials.

Configure the trading pairs, leverage, risk settings, and other parameters as needed.

Download Pre-Trained Models:

Ensure the trained_xgboost_model.pkl and trained_rl_model.zip files are in the project directory. These are the pre-trained models for XGBoost and PPO, respectively.

Configuration

The bot's configuration is stored in config.json. Below are the key parameters:

API Credentials:

Copy

"api_key": "your_api_key",

"api_secret": "your_api_secret"

Trading Pairs:

Copy

"trading_pairs": ["BTCUSDT", "ETHUSDT"]

Leverage and Risk Settings:

Copy

"default_leverage": 20,

"default_risk": 0.01,

"default_risk_percentage": 0.01,

"default_risk_factor": 2,

"default_reward_factor": 6,

"min_risk_to_reward": 3

Model Settings:

Copy

"hybrid_settings": {
  "enable_hybrid_mode": true,
  "xgboost_weight": 0.6,
  "rl_weight": 0.4
}

Running the Bot

The bot can be run in several modes. Use the following commands to start the bot:

Live Trading Mode

To run the bot in live trading mode:

Copy

python run_bot.py --mode=live

This mode connects to Binance via WebSocket and executes trades in real-time.

Ensure your API credentials are correctly configured in config.json.


Backtesting Mode

To run the bot in backtesting mode:


Copy

python run_bot.py --mode=backtest

This mode evaluates the strategy on historical data and generates performance metrics (e.g., Sharpe ratio, max drawdown).

Backtesting results are logged and visualized using an equity curve.

![image alt](https://github.com/jay37749/Ultimate-Crypto-Trading-Bot/blob/97455af8c1a2137a574490c0edc8d70a31ca23b3/trading_bot/BTCUSDT%2035K%2023RD%20JAN%202025%2060%20MONTHS.png)

Retrain XGBoost Model

To retrain the XGBoost model with the latest data:

Copy

python run_bot.py --mode=retrain_xgboost

This mode fetches recent historical data and retrains the XGBoost model.

The retrained model is saved as trained_xgboost_model.pkl.

Live RL Learning Mode

To enable live reinforcement learning:

Copy

python run_bot.py --mode=train_rl


This mode allows the PPO model to learn from real-time market data.

The updated model is saved as trained_rl_model.zip.

Risk Management

The bot includes robust risk management features:

Position Sizing: Calculates the position size based on risk percentage and ATR (Average True Range).

Stop-Loss and Take-Profit: Automatically sets stop-loss and take-profit levels based on risk and reward factors.

Risk-to-Reward Ratio: Skips trades that do not meet the minimum risk-to-reward ratio (configurable in config.json).

![image alt](https://github.com/jay37749/Ultimate-Crypto-Trading-Bot/blob/672bcf077b8bb2f4c1c488769248080ab29f97ae/trading_bot/ETHUSDT%2059K%2023RD%20JAN%202025.png)

Troubleshooting

Common Issues

API Errors:

Ensure your Binance API key and secret are correct.

Check if your IP is whitelisted on Binance.

Data Fetching Errors:

Ensure you have a stable internet connection.

If historical data fetching fails, try reducing the lookback period.

Model Loading Errors:

Ensure the pre-trained models (trained_xgboost_model.pkl and trained_rl_model.zip) are in the correct directory.

Error Logs

Errors are logged in error_log.txt for debugging.

Contributing

Contributions are welcome! If you'd like to improve the bot, please follow these steps:

Fork the repository.

Create a new branch for your feature or bugfix.

Submit a pull request with a detailed description of your changes.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Support

For any questions or issues, please open an issue on the GitHub repository or contact the maintainers.

Happy trading! 🚀

<h3 align="left">Connect with me:</h3>
<p align="left">
</p>

<h3 align="left">Languages and Tools:</h3>
<p align="left"> <a href="https://aws.amazon.com" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/amazonwebservices/amazonwebservices-original-wordmark.svg" alt="aws" width="40" height="40"/> </a> <a href="https://www.cprogramming.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/c/c-original.svg" alt="c" width="40" height="40"/> </a> <a href="https://www.w3schools.com/cpp/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/cplusplus/cplusplus-original.svg" alt="cplusplus" width="40" height="40"/> </a> <a href="https://www.w3schools.com/cs/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/csharp/csharp-original.svg" alt="csharp" width="40" height="40"/> </a> <a href="https://www.docker.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/> </a> <a href="https://dotnet.microsoft.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/dot-net/dot-net-original-wordmark.svg" alt="dotnet" width="40" height="40"/> </a> <a href="https://git-scm.com/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/> </a> <a href="https://www.java.com" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg" alt="java" width="40" height="40"/> </a> <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="40" height="40"/> </a> <a href="https://www.linux.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="linux" width="40" height="40"/> </a> <a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> <a href="https://reactjs.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original-wordmark.svg" alt="react" width="40" height="40"/> </a> </p>

<h3 align="left">Support:</h3>
<p><a href="https://ko-fi.com/https://www.ko-fi.com/powerwellnessdaily"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="https://www.ko-fi.com/powerwellnessdaily" /></a></p><br><br>

<p>&nbsp;<img align="center" src="https://github-readme-stats.vercel.app/api?username=jay37749&show_icons=true&locale=en" alt="jay37749" /></p>
