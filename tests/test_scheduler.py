import unittest
from unittest.mock import patch, MagicMock
import src.scheduler as scheduler_module

class TestScheduler(unittest.TestCase):

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_simple_scheduler_runs_and_keyboard_interrupt(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.minutes.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_simple_scheduler(job_func, interval_minutes=1)
        mock_logging.info.assert_any_call("Scheduler stopped by user")
        job_func.assert_called()

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_simple_scheduler_initial_job_exception(self, mock_logging, mock_schedule):
        job_func = MagicMock(side_effect=Exception("fail"))
        mock_schedule.every.return_value.minutes.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_simple_scheduler(job_func, interval_minutes=1)
        mock_logging.error.assert_any_call("Initial job execution failed: fail", exc_info=True)

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_simple_scheduler_loop_exception(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.minutes.do.return_value = None
        mock_schedule.run_pending.side_effect = [None, Exception("loop fail"), KeyboardInterrupt()]
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_simple_scheduler(job_func, interval_minutes=1)
        mock_logging.error.assert_any_call("Scheduler error: loop fail", exc_info=True)

    @patch('src.scheduler.logging')
    def test_start_manual_trigger_scheduler_success_and_exception(self, mock_logging):
        job_func = MagicMock()
        run_job = scheduler_module.start_manual_trigger_scheduler(job_func)
        run_job()
        mock_logging.info.assert_any_call("Manual job execution completed")
        # Now test exception path
        job_func.side_effect = Exception("fail")
        run_job = scheduler_module.start_manual_trigger_scheduler(job_func)
        run_job()
        mock_logging.error.assert_any_call("Manual job execution failed: fail", exc_info=True)

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_every_minute(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.minute.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_cron_scheduler(job_func, cron_expression="*/1 * * * *")
        mock_logging.info.assert_any_call("Scheduler stopped by user")
        job_func.assert_called()

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_every_hour(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.hour.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_cron_scheduler(job_func, cron_expression="0 * * * *")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_every_day(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.day.at.return_value.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_cron_scheduler(job_func, cron_expression="0 0 * * *")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.logging')
    def test_start_cron_scheduler_unknown_cron(self, mock_logging, mock_schedule):
        job_func = MagicMock()
        mock_schedule.every.return_value.minute.do.return_value = None
        mock_schedule.run_pending.side_effect = KeyboardInterrupt()
        with patch('src.scheduler.time.sleep'):
            scheduler_module.start_cron_scheduler(job_func, cron_expression="not_a_cron")
        mock_logging.warning.assert_any_call("Unknown cron expression: not_a_cron, defaulting to every minute")
        mock_logging.info.assert_any_call("Scheduler stopped by user")

    @patch('src.scheduler.logging')
    def test_start_interval_scheduler_runs_and_keyboard_interrupt(self, mock_logging):
        job_func = MagicMock()
        with patch('src.scheduler.time.sleep', side_effect=[None, KeyboardInterrupt()]):
            scheduler_module.start_interval_scheduler(job_func, seconds=1)
        mock_logging.info.assert_any_call("Scheduler stopped by user")
        job_func.assert_called()

    @patch('src.scheduler.logging')
    def test_start_interval_scheduler_initial_job_exception(self, mock_logging):
        job_func = MagicMock(side_effect=Exception("fail"))
        with patch('src.scheduler.time.sleep', side_effect=[KeyboardInterrupt()]):
            scheduler_module.start_interval_scheduler(job_func, seconds=1)
        mock_logging.error.assert_any_call("Initial job execution failed: fail", exc_info=True)

    @patch('src.scheduler.logging')
    def test_start_interval_scheduler_loop_exception(self, mock_logging):
        job_func = MagicMock(side_effect=[None, Exception("loop fail"), None])
        with patch('src.scheduler.time.sleep', side_effect=[None, None, KeyboardInterrupt()]):
            scheduler_module.start_interval_scheduler(job_func, seconds=1)
        mock_logging.error.assert_any_call("Scheduler error: loop fail", exc_info=True)

    @patch('src.scheduler.logging')
    def test_start_one_time_job_success(self, mock_logging):
        job_func = MagicMock()
        scheduler_module.start_one_time_job(job_func)
        mock_logging.info.assert_any_call("One-time job completed successfully")
        job_func.assert_called_once()

    @patch('src.scheduler.logging')
    def test_start_one_time_job_exception(self, mock_logging):
        job_func = MagicMock(side_effect=Exception("fail"))
        with self.assertRaises(Exception):
            scheduler_module.start_one_time_job(job_func)
        mock_logging.error.assert_any_call("One-time job failed: fail", exc_info=True)

    @patch('src.scheduler.logging')
    def test_start_days_of_month_scheduler_runs_on_specified_day(self, mock_logging):
        job_func = MagicMock()
        # Simulate today is 19th (matches days_of_month)
        class FakeDateTime:
            @classmethod
            def now(cls):
                import datetime
                return datetime.datetime(2025, 6, 19, 0, 0, 0)
            @classmethod
            def date(cls):
                import datetime
                return datetime.date(2025, 6, 19)
        with patch('src.scheduler.datetime') as mock_datetime:
            mock_datetime.datetime = FakeDateTime
            mock_datetime.timedelta = __import__('datetime').timedelta
            # Patch time.sleep to raise KeyboardInterrupt after first loop
            with patch('src.scheduler.time.sleep', side_effect=KeyboardInterrupt()):
                scheduler_module.start_days_of_month_scheduler(job_func, days_of_month=[19])
        mock_logging.info.assert_any_call("Scheduler stopped by user")
        # Should run initial and scheduled job (since last_run_date is updated after initial)
        self.assertGreaterEqual(job_func.call_count, 1)

    @patch('src.scheduler.logging')
    def test_start_days_of_month_scheduler_skips_on_non_matching_day(self, mock_logging):
        job_func = MagicMock()
        # Simulate today is 20th (does not match days_of_month)
        class FakeDateTime:
            @classmethod
            def now(cls):
                import datetime
                return datetime.datetime(2025, 6, 20, 0, 0, 0)
            @classmethod
            def date(cls):
                import datetime
                return datetime.date(2025, 6, 20)
        with patch('src.scheduler.datetime') as mock_datetime:
            mock_datetime.datetime = FakeDateTime
            mock_datetime.timedelta = __import__('datetime').timedelta
            # Patch time.sleep to raise KeyboardInterrupt after first loop
            with patch('src.scheduler.time.sleep', side_effect=KeyboardInterrupt()):
                scheduler_module.start_days_of_month_scheduler(job_func, days_of_month=[19])
        mock_logging.info.assert_any_call("Scheduler stopped by user")
        # Should not run job_func at all
        job_func.assert_not_called()

if __name__ == '__main__':
    unittest.main()