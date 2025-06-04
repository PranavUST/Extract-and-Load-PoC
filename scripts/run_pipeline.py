import sys
from pathlib import Path
from dotenv import load_dotenv
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_ingestion():
    """Run the full pipeline (extract, transform, load)"""
    config_path = "config/api_config.yaml"
    pipeline = DataPipeline(config_path)
    pipeline.run()

if __name__ == "__main__":
    # Configure logging and environment variables
    setup_logging("INFO", "pipeline.log")  # Log to file only
    load_dotenv()  # Load .env variables
    
    # Start the scheduler (runs every 1 minute)
    start_simple_scheduler(run_ingestion, interval_minutes=1)
