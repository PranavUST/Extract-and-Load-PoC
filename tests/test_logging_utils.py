from logging_utils import setup_logging
import logging
import sys
import io

def test_setup_logging_creates_log_file(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(level="DEBUG", log_file=str(log_file))
    logger = logging.getLogger("test_logger")
    logger.debug("debug message")
    logger.info("info message")
    assert log_file.exists()
    # Check log file contains messages
    content = log_file.read_text()
    assert "debug message" in content
    assert "info message" in content

def test_setup_logging_console_output(monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stderr", stream)
    setup_logging(level="INFO")
    logger = logging.getLogger("console_logger")
    logger.info("console info")
    # Flush handlers to ensure output
    for handler in logging.getLogger().handlers:
        handler.flush()
    output = stream.getvalue()
    assert "console info" in output

def test_setup_logging_invalid_level(tmp_path):
    log_file = tmp_path / "invalid_level.log"
    # Should default to INFO if invalid level is given
    setup_logging(level="NOTALEVEL", log_file=str(log_file))
    logger = logging.getLogger("invalid_level_logger")
    logger.info("should appear")
    logger.debug("should not appear")
    content = log_file.read_text()
    assert "should appear" in content
    assert "should not appear" not in content

def test_setup_logging_overwrites_existing_config(tmp_path):
    log_file1 = tmp_path / "log1.log"
    log_file2 = tmp_path / "log2.log"
    setup_logging(level="INFO", log_file=str(log_file1))
    logger = logging.getLogger("overwrite_logger")
    logger.info("first log")
    setup_logging(level="INFO", log_file=str(log_file2))
    logger.info("second log")
    # Only "second log" should appear in log2.log
    content1 = log_file1.read_text()
    content2 = log_file2.read_text()
    assert "first log" in content1
    assert "second log" in content2