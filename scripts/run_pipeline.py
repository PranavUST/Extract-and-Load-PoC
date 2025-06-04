import sys
from pathlib import Path
from dotenv import load_dotenv
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def run_ingestion(config_path: str):
    """Run the full pipeline (extract, transform, load) with the given config."""
    pipeline = DataPipeline(config_path)
    pipeline.run()

def main():
    """Entry point for scheduled execution (default: API config, every 1 min)."""
    setup_logging("INFO", "pipeline.log")
    load_dotenv()
    # You can change the config path here if you want to schedule FTP runs
    start_simple_scheduler(lambda: run_ingestion("config/api_config.yaml"), interval_minutes=1)

if __name__ == "__main__":
    main()
