import data_handler
import ml_model
import risk_management
import order_execution
import logging
from config import API_KEY, API_SECRET
from binance.client import Client

def main():
    logging.basicConfig(level=logging.INFO)
    client = Client(API_KEY, API_SECRET)

    # Example of running data handler
    data_handler.start_websocket()

if __name__ == "__main__":
    main()
