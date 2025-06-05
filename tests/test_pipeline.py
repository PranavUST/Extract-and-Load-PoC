import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os

from src.pipeline import DataPipeline

class TestDataPipeline(unittest.TestCase):

    @patch('src.pipeline.load_config')
    @patch('src.pipeline.resolve_config_vars')
    @patch('src.pipeline.CSVSchemaGenerator')
    def test_init_rest_api(self, mock_schema_gen, mock_resolve, mock_load):
        mock_load.return_value = {'source': {'type': 'REST_API', 'api': {}}, 'destination': {'csv': {}, 'database': {}}}
        mock_resolve.return_value = mock_load.return_value
        pipeline = DataPipeline('dummy_path')
        mock_schema_gen.assert_called_once()  # FIXED: check mock was called
        self.assertTrue(hasattr(pipeline, 'api_client'))

    @patch('src.pipeline.load_config')
    @patch('src.pipeline.resolve_config_vars')
    @patch('src.pipeline.CSVSchemaGenerator')
    def test_init_ftp(self, mock_schema_gen, mock_resolve, mock_load):
        mock_load.return_value = {'source': {'type': 'FTP', 'ftp': {}}, 'destination': {'csv': {}, 'database': {}}}
        mock_resolve.return_value = mock_load.return_value
        pipeline = DataPipeline('dummy_path')
        mock_schema_gen.assert_called_once()  # FIXED: check mock was called
        self.assertTrue(hasattr(pipeline, 'ftp_config'))

    @patch('src.pipeline.logger')
    @patch('src.pipeline.os.makedirs')
    def test_export_to_csv_no_data(self, mock_makedirs, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.export_to_csv([], 'dummy.csv')
        mock_logger.warning.assert_called_with("No data to export")

    @patch('src.pipeline.logger')
    @patch('src.pipeline.os.makedirs')
    @patch('src.pipeline.csv.DictWriter')
    def test_export_to_csv_with_data(self, mock_dictwriter, mock_makedirs, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        data = [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]
        m = mock_open()
        with patch('builtins.open', m):
            pipeline.export_to_csv(data, 'dummy.csv')
        mock_makedirs.assert_called()
        mock_dictwriter.return_value.writeheader.assert_called_once()
        self.assertTrue(mock_dictwriter.return_value.writerow.called)
        mock_logger.info.assert_any_call("Successfully exported %d records to %s", 2, 'dummy.csv')

    @patch('src.pipeline.download_ftp_files')
    @patch('src.pipeline.logger')
    def test_fetch_data_ftp_skip_download(self, mock_logger, mock_download):
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.config = {'source': {'type': 'FTP', 'ftp': {'skip_download': True, 'local_dir': 'ldir'}}, 'destination': {'csv': {}, 'database': {}}}
        pipeline.ftp_config = pipeline.config['source']['ftp']
        pipeline._load_files_from_local = MagicMock(return_value=[{'id': 1}])
        result = pipeline.fetch_data()
        pipeline._load_files_from_local.assert_called_with('ldir')
        self.assertEqual(result, [{'id': 1}])
        mock_logger.info.assert_any_call("Skipping FTP download (local test mode)")

    @patch('src.pipeline.download_ftp_files')
    @patch('src.pipeline.logger')
    def test_fetch_data_ftp_download_fail(self, mock_logger, mock_download):
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.config = {'source': {'type': 'FTP', 'ftp': {'skip_download': False, 'local_dir': 'ldir', 'host': '', 'username': '', 'password': '', 'remote_dir': ''}}, 'destination': {'csv': {}, 'database': {}}}
        pipeline.ftp_config = pipeline.config['source']['ftp']
        pipeline._load_files_from_local = MagicMock()
        mock_download.return_value = []
        result = pipeline.fetch_data()
        mock_logger.error.assert_any_call("FTP download failed. No new files processed.")
        self.assertEqual(result, [])

    @patch('src.pipeline.logger')
    @patch('src.pipeline.os.path.exists', return_value=False)
    def test_load_files_from_local_dir_not_exist(self, mock_exists, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        result = pipeline._load_files_from_local('notadir')
        mock_logger.error.assert_called_with("Local directory does not exist: %s", 'notadir')
        self.assertEqual(result, [])

    @patch('src.pipeline.logger')
    @patch('src.pipeline.os.listdir', return_value=['file.json'])
    @patch('src.pipeline.os.path.exists', return_value=True)
    @patch('src.pipeline.open', new_callable=mock_open, read_data='[{"id":1},{"id":2}]')
    @patch('src.pipeline.json.load', return_value=[{'id': 1}, {'id': 2}])
    def test_load_files_from_local_json(self, mock_jsonload, mock_openfile, mock_exists, mock_listdir, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        result = pipeline._load_files_from_local('adir')
        self.assertEqual(result, [{'id': 1}, {'id': 2}])

    @patch('src.pipeline.logger')
    @patch('src.pipeline.log_pipeline_stats')
    @patch('src.pipeline.load_csv_to_db')
    @patch('src.pipeline.CSVSchemaGenerator')
    @patch('src.pipeline.DataPipeline.export_to_csv')
    @patch('src.pipeline.DataPipeline.fetch_data')
    @patch('src.pipeline.os')
    def test_run_api_success(self, mock_os, mock_fetch, mock_export, mock_schema_gen, mock_load_csv, mock_log_stats, mock_logger):
        # Setup
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.config = {
            'source': {'type': 'REST_API', 'api': {}},
            'destination': {
                'csv': {'output_path': 'file.csv'},
                'database': {'enabled': True}
            }
        }
        mock_fetch.return_value = [{'id': 1}]
        pipeline.schema_generator = MagicMock()

        # Run
        pipeline.run()

        mock_fetch.assert_called_once()
        mock_export.assert_called_once()
        mock_log_stats.assert_called_once()
        mock_logger.info.assert_any_call("DataPipeline execution completed successfully")

    @patch('src.pipeline.logger')
    @patch('src.pipeline.log_pipeline_stats')
    @patch('src.pipeline.load_csv_to_db')
    @patch('src.pipeline.CSVSchemaGenerator')
    @patch('src.pipeline.DataPipeline.export_to_csv')
    @patch('src.pipeline.DataPipeline.fetch_data')
    @patch('src.pipeline.os')
    def test_run_ftp_db_success(self, mock_os, mock_fetch, mock_export, mock_schema_gen, mock_load_csv, mock_log_stats, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.config = {
            'source': {'type': 'FTP', 'ftp': {}},
            'destination': {
                'csv': {'output_path': 'file.csv'},
                'database': {'enabled': True, 'table': 'mytable'}
            }
        }
        mock_fetch.return_value = [{'id': 1}]
        pipeline.schema_generator = MagicMock()
        pipeline.schema_generator.create_pipeline_stats_table = MagicMock()
        pipeline.schema_generator.create_table_from_csv = MagicMock()

        # Run
        pipeline.run()

        mock_fetch.assert_called_once()
        mock_export.assert_called_once()
        pipeline.schema_generator.create_pipeline_stats_table.assert_called()
        pipeline.schema_generator.create_table_from_csv.assert_called()
        mock_load_csv.assert_called_once()
        mock_log_stats.assert_called_once()
        mock_logger.info.assert_any_call("DataPipeline execution completed successfully")

    @patch('src.pipeline.logger')
    @patch('src.pipeline.log_pipeline_stats')
    @patch('src.pipeline.CSVSchemaGenerator')
    @patch('src.pipeline.DataPipeline.export_to_csv')
    @patch('src.pipeline.DataPipeline.fetch_data')
    @patch('src.pipeline.os')
    def test_run_pipeline_exception(self, mock_os, mock_fetch, mock_export, mock_schema_gen, mock_log_stats, mock_logger):
        pipeline = DataPipeline.__new__(DataPipeline)
        pipeline.config = {
            'source': {'type': 'REST_API', 'api': {}},
            'destination': {
                'csv': {'output_path': 'file.csv'},
                'database': {'enabled': True}
            }
        }
        mock_fetch.side_effect = Exception("fail!")
        pipeline.schema_generator = MagicMock()

        with self.assertRaises(Exception):
            pipeline.run()
        mock_log_stats.assert_called_once()
        mock_logger.error.assert_any_call("Pipeline execution failed: %s", "fail!")

if __name__ == '__main__':
    unittest.main()
