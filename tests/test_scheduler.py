import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add the src directory to the path so we can import the scheduler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scheduler import start_scheduler

class TestScheduler(unittest.TestCase):
    
    @patch('scheduler.time.sleep')
    @patch('scheduler.schedule')
    def test_start_scheduler_default_interval(self, mock_schedule, mock_sleep):
        """Test scheduler with default 1-minute interval"""
        # Mock the job function
        mock_job = MagicMock()
        
        # Mock schedule.every() chain
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes
        
        # Mock schedule.run_pending to exit after first call
        call_count = 0
        def side_effect():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:  # Exit after second call
                raise KeyboardInterrupt()
        
        mock_schedule.run_pending.side_effect = side_effect
        
        # Run the scheduler (should exit due to KeyboardInterrupt)
        with self.assertRaises(KeyboardInterrupt):
            start_scheduler(mock_job)
        
        # Verify job was called immediately
        mock_job.assert_called()
        
        # Verify schedule was set up correctly
        mock_schedule.every.assert_called_once_with(1)
        mock_minutes.do.assert_called_once_with(mock_job)
        
        # Verify run_pending was called
        self.assertTrue(mock_schedule.run_pending.called)
        
        # Verify sleep was called
        mock_sleep.assert_called_with(1)

    @patch('scheduler.time.sleep')
    @patch('scheduler.schedule')
    def test_start_scheduler_custom_interval(self, mock_schedule, mock_sleep):
        """Test scheduler with custom interval"""
        mock_job = MagicMock()
        
        # Mock schedule.every() chain
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes
        
        # Exit after first run_pending call
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        
        # Run scheduler with 5-minute interval
        with self.assertRaises(KeyboardInterrupt):
            start_scheduler(mock_job, interval_minutes=5)
        
        # Verify schedule was set up with correct interval
        mock_schedule.every.assert_called_once_with(5)
        mock_minutes.do.assert_called_once_with(mock_job)
        
        # Verify job was called immediately
        mock_job.assert_called_once()

    @patch('scheduler.time.sleep')
    @patch('scheduler.schedule')
    def test_scheduler_job_execution_flow(self, mock_schedule, mock_sleep):
        """Test that job is executed and scheduler runs pending jobs"""
        mock_job = MagicMock()
        
        # Mock schedule chain
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes
        
        # Track calls to run_pending
        run_pending_calls = []
        def track_run_pending():
            run_pending_calls.append(True)
            if len(run_pending_calls) >= 3:  # Exit after 3 calls
                raise KeyboardInterrupt()
        
        mock_schedule.run_pending.side_effect = track_run_pending
        
        # Run scheduler
        with self.assertRaises(KeyboardInterrupt):
            start_scheduler(mock_job, interval_minutes=2)
        
        # Verify job was called immediately (before loop)
        mock_job.assert_called_once()
        
        # Verify run_pending was called multiple times
        self.assertEqual(len(run_pending_calls), 3)
        
        # Verify sleep was called between each run_pending
        expected_sleep_calls = [call(1)] * 2
        mock_sleep.assert_has_calls(expected_sleep_calls)

    @patch('scheduler.logging')
    @patch('scheduler.time.sleep')
    @patch('scheduler.schedule')
    def test_scheduler_logging(self, mock_schedule, mock_sleep, mock_logging):
        """Test that scheduler logs the correct message"""
        mock_job = MagicMock()
        
        # Mock schedule chain
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes
        
        # Exit immediately
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        
        # Run scheduler
        with self.assertRaises(KeyboardInterrupt):
            start_scheduler(mock_job, interval_minutes=3)
        
        # Verify logging was called with correct message
        mock_logging.info.assert_called_with("Scheduling job every 3 minute(s).")

    @patch('scheduler.time.sleep')
    @patch('scheduler.schedule')
    def test_job_function_exception_handling(self, mock_schedule, mock_sleep):
        """Test scheduler behavior when job function raises an exception"""
        # Create a job that raises an exception
        def failing_job():
            raise ValueError("Job failed!")
        
        # Mock schedule chain
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes
        
        # Exit after first run_pending
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        
        # Run scheduler - should not crash when job fails
        with self.assertRaises(KeyboardInterrupt):
            start_scheduler(failing_job)
        
        # Verify schedule was still set up despite job failure
        mock_schedule.every.assert_called_once_with(1)
        mock_minutes.do.assert_called_once_with(failing_job)

if __name__ == '__main__':
    unittest.main()
