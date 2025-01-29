import logging
import os
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, Application
from config import Config
from trading_bot import run_bot
from backtest import run_backtest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch Telegram bot token from the config file
config = Config()
TELEGRAM_TOKEN = config.config_data.get("telegram_bot_token")
AUTHORIZED_USERS = config.config_data.get("authorized_users", [])

if not TELEGRAM_TOKEN:
    raise ValueError("Telegram bot token not provided in the config file.")

# Initialize the bot
bot = Bot(token=TELEGRAM_TOKEN)

# Handlers
def start(update: Update, context: CallbackContext):
    """Send a welcome message and list available commands."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("Unauthorized user. Access denied.")
        return

    message = (
        "Welcome to the Ultimate Crypto Trading Bot!\n\n"
        "Available commands:\n"
        "/status - Get the bot's current status\n"
        "/start_bot - Start the trading bot\n"
        "/stop_bot - Stop the trading bot\n"
        "/backtest - Run a backtest\n"
        "/help - Display this help message"
    )
    update.message.reply_text(message)

def status(update: Update, context: CallbackContext):
    """Provide the current status of the bot."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("Unauthorized user. Access denied.")
        return

    # Placeholder for actual status retrieval
    status_message = "The trading bot is currently running in live mode."
    update.message.reply_text(status_message)

def start_bot(update: Update, context: CallbackContext):
    """Start the trading bot in live mode."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("Unauthorized user. Access denied.")
        return

    update.message.reply_text("Starting the trading bot in live mode...")
    try:
        run_bot(live_trading=True)
    except Exception as e:
        logger.error(f"Error starting the trading bot: {e}")
        update.message.reply_text(f"Failed to start the trading bot: {e}")

def stop_bot(update: Update, context: CallbackContext):
    """Stop the trading bot."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("Unauthorized user. Access denied.")
        return

    update.message.reply_text("Stopping the trading bot...")
    # Implement logic to stop the trading bot (e.g., setting a flag or terminating a process)

def backtest(update: Update, context: CallbackContext):
    """Run a backtest and send results to the user."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("Unauthorized user. Access denied.")
        return

    update.message.reply_text("Running backtest...")
    try:
        run_backtest()
        update.message.reply_text("Backtest completed successfully. Check logs for details.")
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        update.message.reply_text(f"Failed to run backtest: {e}")

def help_command(update: Update, context: CallbackContext):
    """Send a help message."""
    start(update, context)

# Main function to start the Telegram bot
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("start_bot", start_bot))
    dispatcher.add_handler(CommandHandler("stop_bot", stop_bot))
    dispatcher.add_handler(CommandHandler("backtest", backtest))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    logger.info("Starting Telegram bot...")
    main()
