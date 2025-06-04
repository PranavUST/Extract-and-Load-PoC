import logging

def setup_logging(level="INFO", log_file=None):
    """
    Set up logging for the entire system.
    - level: Logging level as a string (e.g., "INFO", "DEBUG").
    - log_file: Optional path to a file to write logs to.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        handlers=handlers,
        force=True  # Overwrites any existing logging config
    )