import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from scripts.api_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_run_pipeline_once(client, monkeypatch):
    # Patch the thread to avoid actually running the pipeline
    monkeypatch.setattr("scripts.api_server.run_pipeline_thread", lambda config_file, run_id=None: None)
    resp = client.post("/run-pipeline-once", json={"config_file": "dummy.yaml"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "started"

def test_run_pipeline_missing_config(client):
    resp = client.post("/run-pipeline", json={})
    assert resp.status_code == 400
    assert "No JSON data provided" in resp.get_json()["message"]

def test_pipeline_status(client, monkeypatch):
    # Patch get_connection to avoid DB access
    monkeypatch.setattr("scripts.api_server.get_connection", lambda: type("Conn", (), {
        "cursor": lambda self: type("Cur", (), {
            "__enter__": lambda s: s,
            "__exit__": lambda s, exc_type, exc_val, exc_tb: None,
            "execute": lambda s, q, p=None: None,
            "fetchall": lambda s: [(None, "msg")]
        })(),
        "close": lambda self: None
    })())
    resp = client.get("/pipeline-status")
    assert resp.status_code == 200
    assert "status" in resp.get_json()

def test_get_saved_source_configs_empty(client, monkeypatch, tmp_path):
    # Patch BASE_DIR to a temp dir with no config file
    monkeypatch.setattr("scripts.api_server.BASE_DIR", str(tmp_path))
    resp = client.get("/saved-source-configs")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_get_current_config_empty(client, monkeypatch, tmp_path):
    monkeypatch.setattr("scripts.api_server.BASE_DIR", str(tmp_path))
    resp = client.get("/current-config")
    assert resp.status_code == 200
    assert resp.get_json() == {"source": None, "target": None}