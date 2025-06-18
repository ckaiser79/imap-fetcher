
import time
from lib.setup_logger import logger

class Retryable:
    def __init__(self, max_retries=3, delay=1):
        self.max_retries = max_retries
        self.delay = delay

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.debug(f"Attempt {attempt + 1} failed: {e}. Retrying in {self.delay} seconds...")
                        time.sleep(self.delay)
                    else:
                        print(f"All attempts failed: {e}")
                        raise
        return wrapper