import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(retries=3, delay=2, exceptions=(Exception,)):
    """
    Decorator to retry a function call with specified retries and delay.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.error("Attempt %d/%d failed: %s", attempt, retries, e)
                    if attempt == retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator