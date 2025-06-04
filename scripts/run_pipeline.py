import sys
from pathlib import Path
from dotenv import load_dotenv
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_smart_scheduler

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_ingestion():
    config_path = project_root / 'config' / 'api_config.yaml'
    pipeline = DataPipeline(str(config_path))
    pipeline.run()

if __name__ == "__main__":
    # Setup logging and environment
    setup_logging(level="INFO", log_file="pipeline.log")
    load_dotenv()

    # Start the smart scheduler
    start_smart_scheduler(
        run_ingestion,
        initial_interval_minutes=1,
        max_interval_minutes=30
    )