import unittest
from unittest.mock import patch, MagicMock, call
from src.scheduler import start_smart_scheduler

class TestScheduler(unittest.TestCase):

    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.schedule')
    def test_start_scheduler_default_interval(self, mock_schedule, mock_sleep):
        """Test scheduler with default 1-minute interval"""
        mock_job = MagicMock()
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes

        call_count = 0
        def side_effect():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise KeyboardInterrupt()
        mock_schedule.run_pending.side_effect = side_effect

        with self.assertRaises(KeyboardInterrupt):
            start_smart_scheduler(mock_job)

        mock_job.assert_called()
        mock_schedule.every.assert_called_once_with(1)
        mock_minutes.do.assert_called_once_with(mock_job)
        self.assertTrue(mock_schedule.run_pending.called)
        mock_sleep.assert_called_with(1)

    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.schedule')
    def test_start_scheduler_custom_interval(self, mock_schedule, mock_sleep):
        """Test scheduler with custom interval"""
        mock_job = MagicMock()
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes

        mock_schedule.run_pending.side_effect = KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            start_smart_scheduler(mock_job, initial_interval_minutes=5)

        mock_schedule.every.assert_called_once_with(5)
        mock_minutes.do.assert_called_once_with(mock_job)
        mock_job.assert_called_once()

    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.schedule')
    def test_scheduler_job_execution_flow(self, mock_schedule, mock_sleep):
        """Test that job is executed and scheduler runs pending jobs"""
        mock_job = MagicMock()
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes

        run_pending_calls = []
        def track_run_pending():
            run_pending_calls.append(True)
            if len(run_pending_calls) >= 3:
                raise KeyboardInterrupt()
        mock_schedule.run_pending.side_effect = track_run_pending

        with self.assertRaises(KeyboardInterrupt):
            start_smart_scheduler(mock_job, initial_interval_minutes=2)

        mock_job.assert_called_once()
        self.assertEqual(len(run_pending_calls), 3)
        expected_sleep_calls = [call(1)] * 2
        mock_sleep.assert_has_calls(expected_sleep_calls)

    @patch('src.scheduler.logging')
    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.schedule')
    def test_scheduler_logging(self, mock_schedule, mock_sleep, mock_logging):
        """Test that scheduler logs the correct message"""
        mock_job = MagicMock()
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes

        mock_schedule.run_pending.side_effect = KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            start_smart_scheduler(mock_job, initial_interval_minutes=3)

        mock_logging.info.assert_called_with("Scheduling job every 3 minute(s).")

    @patch('src.scheduler.time.sleep')
    @patch('src.scheduler.schedule')
    def test_job_function_exception_handling(self, mock_schedule, mock_sleep):
        """Test scheduler behavior when job function raises an exception"""
        def failing_job():
            raise ValueError("Job failed!")
        mock_every = MagicMock()
        mock_minutes = MagicMock()
        mock_schedule.every.return_value = mock_every
        mock_every.minutes = mock_minutes

        mock_schedule.run_pending.side_effect = KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            start_smart_scheduler(failing_job)

        mock_schedule.every.assert_called_once_with(1)
        mock_minutes.do.assert_called_once_with(failing_job)

if __name__ == '__main__':
    unittest.main()