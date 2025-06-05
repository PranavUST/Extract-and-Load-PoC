import pytest
from unittest.mock import Mock, patch, call
import csv
import psycopg2
from pathlib import Path
from src.schema_generator import CSVSchemaGenerator
import logging

@pytest.fixture
def schema_gen():
    return CSVSchemaGenerator()

@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "test.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'age', 'is_active', 'created_at'])
        writer.writerow(['1', 'Alice', '30', 'true', '2023-01-01'])
        writer.writerow(['2', 'Bob', '25', 'false', '2023-01-02'])
    return csv_path

@pytest.fixture
def empty_csv(tmp_path):
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([])
    return csv_path

class TestCSVSchemaGenerator:
    def test_infer_column_type_integer(self, schema_gen):
        values = ['1', '2', '3']
        assert schema_gen.infer_column_type(values) == 'INTEGER'

    def test_infer_column_type_float(self, schema_gen):
        values = ['1.1', '2.5', '3.0']
        assert schema_gen.infer_column_type(values) == 'REAL'

    def test_infer_column_type_boolean(self, schema_gen):
        values = ['true', 'false', '1', '0']
        assert schema_gen.infer_column_type(values) == 'BOOLEAN'

    def test_infer_column_type_timestamp(self, schema_gen):
        values = ['2023-01-01 12:00:00', '2023-01-02 13:30:45']
        assert schema_gen.infer_column_type(values) == 'TIMESTAMP'

    def test_infer_column_type_json(self, schema_gen):
        values = ['{"key": "value"}', '[1, 2, 3]']
        assert schema_gen.infer_column_type(values) == 'JSONB'

    def test_analyze_csv_schema_success(self, schema_gen, sample_csv):
        schema = schema_gen.analyze_csv_schema(sample_csv)
        assert schema == {
            'id': 'INTEGER',
            'name': 'TEXT',
            'age': 'INTEGER',
            'is_active': 'BOOLEAN',
            'created_at': 'TIMESTAMP'
        }

    def test_analyze_csv_schema_empty_file(self, schema_gen, empty_csv):
        with pytest.raises(ValueError):
            schema_gen.analyze_csv_schema(empty_csv)

    def test_generate_create_table_sql_with_id(self, schema_gen):
        columns = {'id': 'INTEGER', 'name': 'TEXT'}
        sql = schema_gen.generate_create_table_sql('users', columns)
        assert '"id" INTEGER PRIMARY KEY' in sql
        assert '"name" TEXT' in sql  # Fixed line
        assert 'CREATE TABLE IF NOT EXISTS "users"' in sql


    def test_generate_create_table_sql_without_id(self, schema_gen):
        columns = {'user_id': 'INTEGER', 'name': 'TEXT'}
        sql = schema_gen.generate_create_table_sql('users', columns)
        assert '"user_id" INTEGER PRIMARY KEY' in sql

    @patch('psycopg2.connect')
    def test_create_table_from_csv_success(self, mock_connect, schema_gen, sample_csv):
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        
        schema_gen.create_table_from_csv(sample_csv, 'test_table', {})
        
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_create_table_from_csv_failure(self, mock_connect, schema_gen, sample_csv):
        mock_connect.side_effect = psycopg2.OperationalError
        with pytest.raises(psycopg2.OperationalError):
            schema_gen.create_table_from_csv(sample_csv, 'test_table', {})

    def test_create_pipeline_stats_table(self, schema_gen):
        mock_execute = Mock()
        schema_gen.execute_query = mock_execute
        
        schema_gen.create_pipeline_stats_table({'dbname': 'test'})
        
        expected_sql = """CREATE TABLE IF NOT EXISTS pipeline_stats (
            stat_date DATE PRIMARY KEY,
            records_fetched INT NOT NULL,
            records_inserted INT NOT NULL,
            error_count INT DEFAULT 0,
            status VARCHAR(50) NOT NULL
        );"""

        # Get the actual call arguments
        args, kwargs = mock_execute.call_args

        # Normalize whitespace for comparison
        actual_sql = args[0].replace('\n', '').replace(' ', '')
        expected_sql_normalized = expected_sql.replace('\n', '').replace(' ', '')

        assert expected_sql_normalized in actual_sql


    def test_boolean_detection(self, schema_gen):
        assert schema_gen._is_boolean('true') is True
        assert schema_gen._is_boolean('FALSE') is True
        assert schema_gen._is_boolean('yes') is True
        assert schema_gen._is_boolean('no') is True
        assert schema_gen._is_boolean('maybe') is False

    def test_json_detection(self, schema_gen):
        assert schema_gen._looks_like_json('{"key": "value"}') is True
        assert schema_gen._looks_like_json('[1, 2, 3]') is True
        assert schema_gen._looks_like_json('not json') is False

    def test_logging(self, schema_gen, sample_csv, caplog):
        with caplog.at_level(logging.INFO):
            schema_gen.analyze_csv_schema(sample_csv)
            assert "Analyzing CSV schema from" in caplog.text
            assert "Schema analysis complete" in caplog.text

    @patch('src.schema_generator.CSVSchemaGenerator.analyze_csv_schema')
    def test_create_table_invalid_schema(self, mock_analyze, schema_gen):
        mock_analyze.side_effect = ValueError("Invalid CSV")
        with pytest.raises(ValueError):
            schema_gen.create_table_from_csv('bad.csv', 'test', {})

    def test_type_mapping_completeness(self, schema_gen):
        assert set(schema_gen.type_mapping.keys()) == {
            'INTEGER', 'REAL', 'BOOLEAN', 
            'TIMESTAMP', 'DATE', 'JSONB', 'TEXT'
        }
