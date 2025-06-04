import pytest
from unittest.mock import patch, MagicMock
from src.database import load_csv_to_db

def test_load_csv_to_db(tmp_path):
    # Prepare a fake CSV file
    csv_content = "id,name,extra\n1,Test,\n,Other,42\n"
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content)

    with patch('src.database.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor

        conn_params = {
            "host": "localhost",
            "port": "5432",
            "dbname": "testdb",
            "user": "user",
            "password": "pass"
        }
        load_csv_to_db(str(csv_path), "api_data", conn_params)

        mock_connect.assert_called_once_with(**conn_params)
        mock_cursor.copy_expert.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()