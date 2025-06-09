import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
from datetime import datetime, timedelta
import threading
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_ingestion(config_path: str):
    """Run the pipeline with the specified config"""
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = (project_root / config_path).resolve()
    pipeline = DataPipeline(config_path)
    pipeline.run()

def main():
    """Entry point for command-line execution."""
    parser = argparse.ArgumentParser(description='Run the data pipeline.')
    parser.add_argument('config', type=str, help='Path to the configuration file (e.g., config/api_config.yaml)')
    parser.add_argument('--interval', type=int, default=2, help='Interval in minutes between pipeline runs')
    parser.add_argument('--duration', type=float, required=True, help='Total duration in hours to keep running')
    args = parser.parse_args()

    setup_logging("INFO", "pipeline.log")
    load_dotenv()

    end_time = datetime.now() + timedelta(hours=args.duration)

    def scheduled_task():
        if datetime.now() <= end_time:
            run_ingestion(args.config)
        else:
            print("Duration complete. Stopping scheduler.")
            # Stop the scheduler by raising SystemExit in the main thread
            threading.Thread(target=lambda: sys.exit(0)).start()

    start_simple_scheduler(scheduled_task, interval_minutes=args.interval)

if __name__ == "__main__":
    main()