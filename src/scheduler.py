import time
import datetime
import logging
import hashlib
import json
import os

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def start_smart_scheduler(job_func, initial_interval_minutes=1, max_interval_minutes=30):
    """
    Smart scheduler that increases sleep time when no new data is found.
    """
    logging.info("Starting smart scheduler with adaptive intervals")
    current_interval = initial_interval_minutes
    last_data_hash = None
    state_file = "./data/scheduler_state.json"

    # Load last known state
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                last_data_hash = state.get('last_data_hash')
    except Exception as e:
        logging.warning(f"Could not load scheduler state: {e}")

    while True:
        try:
            current_data_hash = get_current_data_hash()
            if current_data_hash != last_data_hash:
                logging.info("New data detected, running job")
                job_func()
                last_data_hash = current_data_hash

                # Save state
                os.makedirs(os.path.dirname(state_file), exist_ok=True)
                with open(state_file, 'w') as f:
                    json.dump({'last_data_hash': last_data_hash}, f)

                current_interval = initial_interval_minutes
                logging.info(f"Job completed, next check in {current_interval} minutes")
            else:
                current_interval = min(current_interval * 2, max_interval_minutes)
                logging.info(f"No new data, sleeping for {current_interval} minutes")

            time.sleep(current_interval * 60)

        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user\n")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error

def get_current_data_hash():
    """
    Get a hash of the current data to detect changes.
    Uses the correct source type (API or FTP).
    """
    try:
        from src.config_loader import load_config, resolve_config_vars
        config = resolve_config_vars(load_config("config/api_config.yaml"))
        source_type = config['source']['type']

        if source_type == "REST_API":
            from src.api_client import APIClient
            client = APIClient(config['source']['api'])
            data = client.fetch_data()
        elif source_type == "FTP":
            from src.pipeline import DataPipeline
            pipeline = DataPipeline("config/api_config.yaml")
            data = pipeline.fetch_data()
        else:
            raise ValueError(f"Unknown source type: {source_type}")

        data_str = json.dumps(data, sort_keys=True, cls=EnhancedJSONEncoder)
        return hashlib.md5(data_str.encode()).hexdigest()
    except Exception as e:
        logging.warning(f"Could not get current data hash: {e}")
        return None