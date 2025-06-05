import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from ftp_client import download_ftp_files

@pytest.fixture
def ftp_mock(monkeypatch):
    ftp_instance = MagicMock()
    ftp_class = MagicMock()
    ftp_class.return_value.__enter__.return_value = ftp_instance
    monkeypatch.setattr("ftplib.FTP", ftp_class)
    return ftp_instance

def test_download_success(tmp_path, ftp_mock):
    ftp_mock.nlst.return_value = ["file1.txt", "file2.csv"]
    ftp_mock.retrbinary.side_effect = lambda cmd, cb: cb(b"data")
    local_dir = tmp_path / "downloads"
    result = download_ftp_files(
        host="host", username="user", password="pass",
        remote_dir="/remote", local_dir=str(local_dir)
    )
    assert len(result) == 2
    assert os.path.exists(result[0])
    assert os.path.exists(result[1])
    assert ftp_mock.login.called
    assert ftp_mock.cwd.called

def test_download_with_file_types(tmp_path, ftp_mock):
    ftp_mock.nlst.return_value = ["file1.txt", "file2.csv", "file3.log"]
    ftp_mock.retrbinary.side_effect = lambda cmd, cb: cb(b"data")
    local_dir = tmp_path / "downloads"
    result = download_ftp_files(
        host="host", username="user", password="pass",
        remote_dir="/remote", local_dir=str(local_dir),
        file_types=[".csv", ".log"]
    )
    assert len(result) == 2
    assert result[0].endswith("file2.csv")
    assert result[1].endswith("file3.log")

def test_download_skips_existing_files(tmp_path, ftp_mock):
    ftp_mock.nlst.return_value = ["file1.txt"]
    ftp_mock.retrbinary.side_effect = lambda cmd, cb: cb(b"data")
    local_dir = tmp_path / "downloads"
    os.makedirs(local_dir, exist_ok=True)
    existing_file = local_dir / "file1.txt"
    existing_file.write_text("already here")
    result = download_ftp_files(
        host="host", username="user", password="pass",
        remote_dir="/remote", local_dir=str(local_dir)
    )
    assert len(result) == 0  # Should skip existing file

def test_download_permission_error(tmp_path, ftp_mock):
    local_dir = tmp_path / "downloads"
    # Simulate unwritable directory
    with patch("os.access", return_value=False):
        result = download_ftp_files(
            host="host", username="user", password="pass",
            remote_dir="/remote", local_dir=str(local_dir)
        )
    assert result == []

def test_download_ftp_perm_error(tmp_path, ftp_mock):
    ftp_mock.login.side_effect = Exception("530 Login incorrect.")
    local_dir = tmp_path / "downloads"
    with patch("ftplib.FTP", side_effect=Exception("530 Login incorrect.")):
        result = download_ftp_files(
            host="host", username="user", password="pass",
            remote_dir="/remote", local_dir=str(local_dir)
        )
    assert result == []

def test_download_retries_on_exception(tmp_path, monkeypatch):
    call_count = {"n": 0}
    def fake_ftp(*args, **kwargs):
        class FakeFTP:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
            def login(self, *a, **k): pass
            def cwd(self, *a, **k): pass
            def nlst(self): return ["file1.txt"]
            def retrbinary(self, cmd, cb):
                call_count["n"] += 1
                raise Exception("Temporary error")
        return FakeFTP()
    monkeypatch.setattr("ftplib.FTP", fake_ftp)
    monkeypatch.setattr("os.path.exists", lambda path: False)  # Always force download
    local_dir = tmp_path / "downloads"
    result = download_ftp_files(
        host="host", username="user", password="pass",
        remote_dir="/remote", local_dir=str(local_dir),
        retries=2, delay=0
    )
    assert result == []
    assert call_count["n"] == 2