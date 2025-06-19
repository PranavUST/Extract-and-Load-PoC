import sys
import uuid
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from dotenv import load_dotenv
import argparse
from datetime import datetime, timedelta
import threading
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler
from src.database import create_logins_table_if_not_exists  # New import
from src.database import create_logins_table_if_not_exists, create_pipeline_status_table_if_not_exists

def run_ingestion(config_path: str, run_id: str = None):
    """Run the pipeline with the specified config"""
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = (project_root / config_path).resolve()
    
    # Auto-create logins and pipeline_status tables before pipeline execution
    create_logins_table_if_not_exists()
    create_pipeline_status_table_if_not_exists()

    if run_id is None:
        run_id = str(uuid.uuid4())

    run_id_path = project_root / "latest_scheduled_run_id.txt"
    with open(run_id_path, "w") as f:
        f.write(run_id)
    
    pipeline = DataPipeline(config_path)
    pipeline.run(run_id=run_id)

def main():
    """Entry point for command-line execution."""
    parser = argparse.ArgumentParser(description='Run the data pipeline.')
    parser.add_argument('config', type=str, help='Path to the configuration file (e.g., config/api_config.yaml)')
    parser.add_argument('--interval', type=int, help='Interval in minutes between pipeline runs')
    parser.add_argument('--duration', type=float, help='Total duration in hours to keep running')
    parser.add_argument('--hourly', action='store_true', help='Run once every hour')
    parser.add_argument('--days-of-month', type=str, help='Comma-separated days of month (e.g. 1,15,28)')
    args = parser.parse_args()

    setup_logging("INFO", "pipeline.log")
    load_dotenv()

    if args.days_of_month:
        # Days of month scheduler
        days = [int(day.strip()) for day in args.days_of_month.split(',') if day.strip().isdigit()]
        def scheduled_task():
            run_ingestion(args.config)
        from src.scheduler import start_days_of_month_scheduler
        start_days_of_month_scheduler(scheduled_task, days)
    elif args.hourly:
        # Hourly scheduler
        if not args.duration:
            print("Duration is required for hourly schedule.")
            sys.exit(1)
        end_time = datetime.now() + timedelta(hours=args.duration)
        def scheduled_task():
            if datetime.now() <= end_time:
                run_ingestion(args.config)
            else:
                print("Duration complete. Stopping scheduler.")
                threading.Thread(target=lambda: sys.exit(0)).start()
        from src.scheduler import start_simple_scheduler
        start_simple_scheduler(scheduled_task, interval_minutes=60)
    elif args.interval:
        # Interval scheduler
        if not args.duration:
            print("Duration is required for interval schedule.")
            sys.exit(1)
        end_time = datetime.now() + timedelta(hours=args.duration)
        def scheduled_task():
            if datetime.now() <= end_time:
                run_ingestion(args.config)
            else:
                print("Duration complete. Stopping scheduler.")
                threading.Thread(target=lambda: sys.exit(0)).start()
        from src.scheduler import start_simple_scheduler
        start_simple_scheduler(scheduled_task, interval_minutes=args.interval)
    else:
        # Default: run once
        run_ingestion(args.config)

if __name__ == "__main__":
    main()