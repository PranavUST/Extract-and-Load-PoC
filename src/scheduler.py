import time
import logging
import schedule

<<<<<<< Updated upstream
def start_smart_scheduler(job_func, initial_interval_minutes=1, max_interval_minutes=30):
    """
    Smart scheduler that increases sleep time when no new data is found
    """
    logging.info("Starting smart scheduler with adaptive intervals")
    
    current_interval = initial_interval_minutes
    last_data_hash = None
    state_file = "./data/scheduler_state.json"
    
    # Load last known state
=======
logger = logging.getLogger(__name__)

def start_simple_scheduler(job_func, interval_minutes=1):
    """
    Simple scheduler that runs the job at regular intervals
    Uses UPSERT in database to handle duplicates gracefully
    """
    logging.info(f"Starting simple scheduler - runs every {interval_minutes} minute(s)")
    
    # Schedule the job
    schedule.every(interval_minutes).minutes.do(job_func)
    
    # Run once immediately
>>>>>>> Stashed changes
    try:
        logging.info("Running initial pipeline execution")
        job_func()
    except Exception as e:
<<<<<<< Updated upstream
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
            
=======
        logging.error(f"Initial job execution failed: {e}", exc_info=True)
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
>>>>>>> Stashed changes
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error

def start_manual_trigger_scheduler(job_func):
    """
<<<<<<< Updated upstream
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
=======
    Alternative: Manual trigger scheduler
    Only runs when you manually trigger it
    """
    logging.info("Manual trigger scheduler ready - call run_job() to execute")
    
    def run_job():
        try:
            logging.info("Manual job execution triggered")
            job_func()
            logging.info("Manual job execution completed")
        except Exception as e:
            logging.error(f"Manual job execution failed: {e}", exc_info=True)
    
    return run_job
>>>>>>> Stashed changes
