import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_ingestion(config_path: str):
    """Run the pipeline with the specified config"""
    pipeline = DataPipeline(config_path)
    pipeline.run()

def main():
    """Entry point for command-line execution."""
    parser = argparse.ArgumentParser(description='Run the data pipeline.')
    parser.add_argument('config', type=str, help='Path to the configuration file (e.g., config/api_config.yaml)')
    args = parser.parse_args()

    setup_logging("INFO", "pipeline.log")
    load_dotenv()
    
    # Start scheduler with the provided config
    start_simple_scheduler(lambda: run_ingestion(args.config), interval_minutes=1)

if __name__ == "__main__":
    main()
