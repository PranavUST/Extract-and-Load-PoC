import time
import logging
import hashlib
import json
import os

def start_smart_scheduler(job_func, initial_interval_minutes=1, max_interval_minutes=30):
    """
    Smart scheduler that increases sleep time when no new data is found
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
            # Check if there's new data before running the job
            current_data_hash = get_current_data_hash()
            
            if current_data_hash != last_data_hash:
                logging.info("New data detected, running job")
                job_func()
                last_data_hash = current_data_hash
                
                # Save state
                os.makedirs(os.path.dirname(state_file), exist_ok=True)
                with open(state_file, 'w') as f:
                    json.dump({'last_data_hash': last_data_hash}, f)
                
                # Reset interval on successful processing
                current_interval = initial_interval_minutes
                logging.info(f"Job completed, next check in {current_interval} minutes")
            else:
                # No new data, increase sleep interval
                current_interval = min(current_interval * 2, max_interval_minutes)
                logging.info(f"No new data, sleeping for {current_interval} minutes")
            
            # Sleep for the current interval
            time.sleep(current_interval * 60)
            
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error

def get_current_data_hash():
    """
    Get a hash of the current data to detect changes
    You'll need to implement this based on your data source
    """
    try:
        from api_client import APIClient
        from config_loader import load_config, resolve_config_vars
        
        config = resolve_config_vars(load_config("config/api_config.yaml"))
        client = APIClient(config['source']['api'])
        data = client.fetch_data()
        
        # Create hash of the data
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    except Exception as e:
        logging.warning(f"Could not get current data hash: {e}")
        return None
