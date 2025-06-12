import pytest
from unittest.mock import patch, MagicMock
import os

import database as db

@pytest.fixture
def conn_params():
    return {
        "host": "localhost",
        "port": "5432",
        "dbname": "testdb",
        "user": "user",
        "password": "pass"
    }

def test_get_connection(monkeypatch):
    mock_connect = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", mock_connect)
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "p")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "pw")
    db.get_connection()
    mock_connect.assert_called_once_with(
        host="h", port="p", dbname="n", user="u", password="pw"
    )

def test_load_csv_to_db(tmp_path, conn_params):
    csv_content = "id,name\n1,Test\n2,Other\n"
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content)
    with patch("database.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        db.load_csv_to_db(str(csv_path), "api_data", conn_params)
        mock_connect.assert_called_once_with(**conn_params)
        mock_cursor.executemany.assert_called()
        mock_conn.commit.assert_called_once()

def test_load_csv_to_db_empty_columns(tmp_path, conn_params, caplog):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("")
    with patch("database.psycopg2.connect"):
        db.load_csv_to_db(str(csv_path), "api_data", conn_params)
        assert "CSV file has no columns" in caplog.text

def test_load_csv_to_db_exception(tmp_path, conn_params):
    csv_content = "id,name\n1,Test\n"
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content)
    with patch("database.psycopg2.connect", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            db.load_csv_to_db(str(csv_path), "api_data", conn_params)

def test_execute_query_select(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("a",)]
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    result = db.execute_query("SELECT * FROM t", conn_params=conn_params)
    assert result == [("a",)]
    mock_conn.close.assert_called_once()

def test_execute_query_nonselect(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    result = db.execute_query("UPDATE t SET x=1", conn_params=conn_params)
    assert result is None
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_execute_query_exception(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("fail")
    with pytest.raises(Exception):
        db.execute_query("SELECT * FROM t", conn_params=conn_params)
    mock_conn.close.assert_called()

def test_table_exists_true(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(return_value=[(True,)]))
    assert db.table_exists("t", conn_params=conn_params) is True

def test_table_exists_false(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(return_value=[(False,)]))
    assert db.table_exists("t", conn_params=conn_params) is False

def test_table_exists_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(side_effect=Exception("fail")))
    assert db.table_exists("t", conn_params=conn_params) is False

def test_drop_table(monkeypatch, conn_params):
    mock_execute = MagicMock()
    monkeypatch.setattr(db, "execute_query", mock_execute)
    db.drop_table("t", conn_params=conn_params)
    assert mock_execute.called

def test_drop_table_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(side_effect=Exception("fail")))
    with pytest.raises(Exception):
        db.drop_table("t", conn_params=conn_params)

def test_get_table_row_count(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(return_value=[(42,)]))
    assert db.get_table_row_count("t", conn_params=conn_params) == 42

def test_get_table_row_count_none(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(return_value=None))
    assert db.get_table_row_count("t", conn_params=conn_params) == 0

def test_get_table_row_count_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db, "execute_query", MagicMock(side_effect=Exception("fail")))
    assert db.get_table_row_count("t", conn_params=conn_params) == 0

def test_log_pipeline_stats(monkeypatch, conn_params):
    mock_execute = MagicMock()
    monkeypatch.setattr(db, "execute_query", mock_execute)
    # Patch CSVSchemaGenerator and its method at the correct import path
    mock_schema_gen = MagicMock()
    mock_schema_gen.create_pipeline_stats_table = MagicMock()
    monkeypatch.setattr("src.schema_generator.CSVSchemaGenerator", lambda *a, **kw: mock_schema_gen)
    stats = {"records_fetched": 1, "records_inserted": 2, "error_count": 0, "status": "ok"}
    db.log_pipeline_stats(stats, conn_params)
    assert mock_execute.called

def test_log_pipeline_stats_no_conn_params(caplog):
    stats = {"records_fetched": 1, "records_inserted": 2, "error_count": 0, "status": "ok"}
    db.log_pipeline_stats(stats, None)
    assert "No connection parameters provided for stats logging" in caplog.text

def test_log_pipeline_stats_exception(monkeypatch, conn_params, caplog):
    # Patch CSVSchemaGenerator to raise
    monkeypatch.setattr("src.schema_generator.CSVSchemaGenerator", MagicMock(side_effect=Exception("fail")))
    stats = {"records_fetched": 1, "records_inserted": 2, "error_count": 0, "status": "ok"}
    db.log_pipeline_stats(stats, conn_params)
    assert "Stats logging failed: fail" in caplog.text

def test_create_logins_table_if_not_exists(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    db.create_logins_table_if_not_exists(conn_params)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

def test_create_logins_table_if_not_exists_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(side_effect=Exception("fail")))
    with pytest.raises(Exception):
        db.create_logins_table_if_not_exists(conn_params)

def test_create_pipeline_status_table_if_not_exists(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    db.create_pipeline_status_table_if_not_exists(conn_params)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

def test_create_pipeline_status_table_if_not_exists_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(side_effect=Exception("fail")))
    with pytest.raises(Exception):
        db.create_pipeline_status_table_if_not_exists(conn_params)

def test_insert_pipeline_status(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    db.insert_pipeline_status("msg", "runid", conn_params)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

def test_insert_pipeline_status_no_runid(monkeypatch, conn_params):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(return_value=mock_conn))
    mock_conn.cursor.return_value = mock_cursor
    db.insert_pipeline_status("msg", None, conn_params)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

def test_insert_pipeline_status_exception(monkeypatch, conn_params):
    monkeypatch.setattr(db.psycopg2, "connect", MagicMock(side_effect=Exception("fail")))
    with pytest.raises(Exception):
        db.insert_pipeline_status("msg", "runid", conn_params)