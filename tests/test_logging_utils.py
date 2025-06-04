from src.logging_utils import setup_logging
import logging

def test_setup_logging(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(level="DEBUG", log_file=str(log_file))
    logger = logging.getLogger("test_logger")
    logger.debug("debug message")
    logger.info("info message")
    # Check if file was created
    assert log_file.exists()