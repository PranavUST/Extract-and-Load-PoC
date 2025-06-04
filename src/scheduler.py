import time
import logging
import schedule

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
    try:
        logging.info("Running initial pipeline execution")
        job_func()
    except Exception as e:
        logging.error(f"Initial job execution failed: {e}", exc_info=True)
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error

def start_manual_trigger_scheduler(job_func):
    """
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

def start_cron_scheduler(job_func, cron_expression="*/1 * * * *"):
    """
    Cron-style scheduler for more complex scheduling
    Default: every minute
    """
    logging.info(f"Starting cron scheduler with expression: {cron_expression}")
    
    # Parse common cron expressions
    if cron_expression == "*/1 * * * *":  # Every minute
        schedule.every().minute.do(job_func)
    elif cron_expression == "0 * * * *":  # Every hour
        schedule.every().hour.do(job_func)
    elif cron_expression == "0 0 * * *":  # Every day at midnight
        schedule.every().day.at("00:00").do(job_func)
    else:
        # Default to every minute if unknown pattern
        logging.warning(f"Unknown cron expression: {cron_expression}, defaulting to every minute")
        schedule.every().minute.do(job_func)
    
    # Run once immediately
    try:
        logging.info("Running initial pipeline execution")
        job_func()
    except Exception as e:
        logging.error(f"Initial job execution failed: {e}", exc_info=True)
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)

def start_interval_scheduler(job_func, seconds=60):
    """
    Scheduler that runs at specific second intervals
    """
    logging.info(f"Starting interval scheduler - runs every {seconds} seconds")
    
    # Run once immediately
    try:
        logging.info("Running initial pipeline execution")
        job_func()
    except Exception as e:
        logging.error(f"Initial job execution failed: {e}", exc_info=True)
    
    # Main loop
    while True:
        try:
            time.sleep(seconds)
            logging.info("Running scheduled pipeline execution")
            job_func()
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error

def start_one_time_job(job_func):
    """
    Run the job just once
    """
    logging.info("Running one-time job execution")
    try:
        job_func()
        logging.info("One-time job completed successfully")
    except Exception as e:
        logging.error(f"One-time job failed: {e}", exc_info=True)
        raise
