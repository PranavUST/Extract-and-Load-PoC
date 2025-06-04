import logging
import sys
import logging
from pathlib import Path
<<<<<<< Updated upstream
=======
from dotenv import load_dotenv
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline
from src.scheduler import start_simple_scheduler
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.logging_utils import setup_logging
from src.pipeline import DataPipeline

logger = logging.getLogger(__name__)

def main():
    # Setup logging first
    setup_logging(level="INFO", log_file="pipeline.log")
    logger.info("Starting pipeline execution script")
    
    # Load environment variables
    load_dotenv()
    logger.debug("Environment variables loaded from .env file")
    
    try:
        config_path = project_root / 'config' / 'api_config.yaml'
        logger.info("Using config file: %s", config_path)
        
        if not config_path.exists():
            logger.error("Config file not found: %s", config_path)
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        logger.info("Initializing DataPipeline")
        pipeline = DataPipeline(str(config_path))
        
        logger.info("Starting pipeline execution")
        pipeline.run()
        logger.info("Pipeline execution completed successfully")
        
    except FileNotFoundError as e:
        logger.error("Configuration file error: %s", str(e))
        raise
    except Exception as e:
        logger.error("Pipeline execution failed: %s", str(e))
        logger.debug("Pipeline failure details", exc_info=True)
        raise

import logging
from pipeline import DataPipeline
from scheduler import start_smart_scheduler  # or start_file_watcher_scheduler

def run_ingestion():
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    config_path = "config/api_config.yaml"
    pipeline = DataPipeline(config_path)
    pipeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Use smart scheduler that adapts based on data changes
    start_smart_scheduler(
        run_ingestion, 
        initial_interval_minutes=1,    # Start checking every minute
        max_interval_minutes=30        # Max wait time when no data changes
    )
=======
    """
    Simple ingestion function - always runs full pipeline
    UPSERT in database handles duplicates gracefully
    """
    config_path = "config/api_config.yaml"
    pipeline = DataPipeline(config_path)
    pipeline.run()  # Always run full pipeline

if __name__ == "__main__":
=======
    """
    Simple ingestion function - always runs full pipeline
    UPSERT in database handles duplicates gracefully
    """
    config_path = "config/api_config.yaml"
    pipeline = DataPipeline(config_path)
    pipeline.run()  # Always run full pipeline

if __name__ == "__main__":
>>>>>>> Stashed changes
    # Configure logging to file only
    setup_logging("INFO", "pipeline.log")
    
    # Use simple scheduler - no complex state management
    start_simple_scheduler(run_ingestion, interval_minutes=1)
<<<<<<< Updated upstream
    
>>>>>>> Stashed changes
=======
    
>>>>>>> Stashed changes
