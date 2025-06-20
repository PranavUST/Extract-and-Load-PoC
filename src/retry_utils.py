import time
import logging
from functools import wraps
from src.database import insert_pipeline_status

logger = logging.getLogger(__name__)

def retry_call(func, retries=3, delay=2, exceptions=(Exception,), run_id=None, *args, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            # Only insert for retry attempts
            insert_pipeline_status(f"Attempt {attempt}/{retries} failed: {e}", run_id=run_id, log_level="ERROR", module="retry_utils")
            if attempt == retries:
                raise
            time.sleep(delay)

def retry(retries=3, delay=2, exceptions=(Exception,), run_id=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # Only insert for retry attempts
                    insert_pipeline_status(f"Attempt {attempt}/{retries} failed: {e}", run_id=run_id, log_level="ERROR", module="retry_utils")
                    if attempt == retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator