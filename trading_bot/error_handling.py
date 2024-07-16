import logging
from retrying import retry

logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def handle_error(error):
    logging.error(f"Error occurred: {error}")

@retry(wait_fixed=2000, stop_max_attempt_number=5)
def execute_with_retry(func, *args, **kwargs):
    return func(*args, **kwargs)
