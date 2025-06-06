import logging

def setup_logging(level="INFO", log_file=None):
    """
    Set up logging for the entire system.
    - level: Logging level as a string (e.g., "INFO", "DEBUG").
    - log_file: Optional path to a file to write logs to.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True
    )