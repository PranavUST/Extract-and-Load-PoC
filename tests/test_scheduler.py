import unittest
from unittest.mock import patch, MagicMock, call
import logging
import schedule
import time

import src.scheduler as scheduler_module

class TestScheduler(unittest.TestCase):

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_simple_scheduler_runs_and_handles_exceptions(self, mock_logging, mock_schedule):
        # Arrange
        job_func = MagicMock()
        mock_schedule.every.return_value.minutes.do.return_value = None

        # Simulate KeyboardInterrupt after first run_pending
        def run_pending_side_effect():
            raise KeyboardInterrupt()
        mock_schedule.run_pending.side_effect = run_pending_side_effect

        # Act
        scheduler_module.start_simple_scheduler(job_func, interval_minutes=2)

        # Assert
        job_func.assert_called_once()
        mock_schedule.every.assert_called_once_with(2)
        mock_logging.info.assert_any_call("Starting simple scheduler - runs every 2 minute(s)")
        mock_logging.info.assert_any_call("Running initial pipeline execution")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_simple_scheduler_initial_job_exception(self, mock_logging, mock_schedule):
        # Arrange
        def failing_job():
            raise ValueError("fail!")
        mock_schedule.every.return_value.minutes.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt

        # Act
        scheduler_module.start_simple_scheduler(failing_job, interval_minutes=1)

        # Assert
        mock_logging.error.assert_any_call("Initial job execution failed: fail!", exc_info=True)

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_every_minute(self, mock_logging, mock_schedule):
        # Arrange
        job_func = MagicMock()
        mock_schedule.every.return_value.minute.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt

        # Act
        scheduler_module.start_cron_scheduler(job_func, cron_expression="*/1 * * * *")

        # Assert
        job_func.assert_called_once()
        mock_logging.info.assert_any_call("Starting cron scheduler with expression: */1 * * * *")
        mock_logging.info.assert_any_call("Running initial pipeline execution")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_unknown_pattern(self, mock_logging, mock_schedule):
        # Arrange
        job_func = MagicMock()
        mock_schedule.every.return_value.minute.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt

        # Act
        scheduler_module.start_cron_scheduler(job_func, cron_expression="foo")

        # Assert
        mock_logging.warning.assert_any_call("Unknown cron expression: foo, defaulting to every minute")

    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.logging')
    def test_start_interval_scheduler_runs_and_handles_exceptions(self, mock_logging, mock_sleep):
        # Arrange
        job_func = MagicMock()
        def sleep_side_effect(seconds):
            raise KeyboardInterrupt()
        mock_sleep.side_effect = sleep_side_effect

        # Act
        scheduler_module.start_interval_scheduler(job_func, seconds=5)

        # Assert
        job_func.assert_called_once()
        mock_logging.info.assert_any_call("Starting interval scheduler - runs every 5 seconds")
        mock_logging.info.assert_any_call("Running initial pipeline execution")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    # Rest of the test methods remain unchanged as they don't involve KeyboardInterrupt handling

if __name__ == '__main__':
    unittest.main()
