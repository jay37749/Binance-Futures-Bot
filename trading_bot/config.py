import json
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config_data = {}
        self.load_config()

    def load_config(self):
        """
        Load configuration from the JSON file.
        """
        try:
            with open(self.config_file_path) as config_file:
                self.config_data = json.load(config_file)
                logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def reload_config(self):
        """
        Reload the configuration file dynamically.
        """
        try:
            self.load_config()
            logger.info("Configuration reloaded successfully.")
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")

    # Fetch API credentials
    def get_api_credentials(self):
        return self.config_data['api_key'], self.config_data['api_secret']

    # Fetch trading pairs
    def get_trading_pairs(self):
        return self.config_data['trading_pairs']

    # Fetch leverage settings
    def get_leverage_settings(self, pair=None):
        if pair and 'pair_specific' in self.config_data and pair in self.config_data['pair_specific']:
            return self.config_data['pair_specific'][pair].get('leverage', self.config_data['default_leverage'])
        return self.config_data.get('default_leverage', 20)

    # Fetch risk percentage
    def get_risk_percentage(self, pair=None):
        if pair and 'pair_specific' in self.config_data and pair in self.config_data['pair_specific']:
            return self.config_data['pair_specific'][pair].get('risk_percentage', self.config_data['default_risk_percentage'])
        return self.config_data.get('default_risk_percentage', 0.01)

    # Fetch risk factor
    def get_risk_factor(self):
        return self.config_data.get('default_risk_factor', 2)

    # Fetch reward factor
    def get_reward_factor(self):
        return self.config_data.get('default_reward_factor', 6)

    # Fetch minimum risk-to-reward ratio
    def get_min_risk_to_reward(self):
        return self.config_data.get('min_risk_to_reward', 3)

    # Fetch trading strategy
    def get_strategy(self, pair=None):
        if pair and 'pair_specific' in self.config_data and pair in self.config_data['pair_specific']:
            return self.config_data['pair_specific'][pair].get('strategy', self.config_data['default_strategy'])
        return self.config_data.get('default_strategy', 'hybrid')

    # Fetch polling interval
    def get_polling_interval(self):
        return self.config_data.get('polling_interval', 60)

    # Fetch RL hyperparameters
    def get_rl_hyperparameters(self):
        return {
            'learning_rate': self.config_data['rl_hyperparameters'].get('learning_rate', 0.001),
            'gamma': self.config_data['rl_hyperparameters'].get('gamma', 0.99),
            'epsilon_start': self.config_data['rl_hyperparameters'].get('epsilon_start', 1.0),
            'epsilon_end': self.config_data['rl_hyperparameters'].get('epsilon_end', 0.1),
            'epsilon_decay': self.config_data['rl_hyperparameters'].get('epsilon_decay', 0.995)
        }

    # Fetch hybrid mode settings
    def get_hybrid_settings(self):
        return {
            'enable_hybrid_mode': self.config_data.get('enable_hybrid_mode', True),
            'xgboost_weight': self.config_data['hybrid_settings'].get('xgboost_weight', 0.5),
            'rl_weight': self.config_data['hybrid_settings'].get('rl_weight', 0.5)
        }

    # Fetch model-specific adjustments
    def get_model_adjustments(self, model_type):
        return self.config_data['model_adjustments'].get(model_type, {})

    # Fetch Telegram bot token
    def get_telegram_bot_token(self):
        return self.config_data.get('telegram_bot_token', '')

    # Fetch authorized Telegram users
    def get_authorized_users(self):
        return self.config_data.get('authorized_users', [])
