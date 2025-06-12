import tempfile
import os
from src.pipeline import DataPipeline

def test_pipeline_end_to_end(monkeypatch):
    # Prepare a minimal config dict for the pipeline
    config = {
        "source": {"type": "REST_API", "api": {"endpoint": "dummy", "token": "dummy"}},
        "destination": {"csv": {"output_path": "test_output.csv"}, "database": {}}
    }
    # Patch load_config and resolve_config_vars to return our config
    monkeypatch.setattr("src.pipeline.load_config", lambda path: config)
    monkeypatch.setattr("src.pipeline.resolve_config_vars", lambda c: c)
    # Patch API client to return dummy data
    monkeypatch.setattr("src.api_client.APIClient.fetch_data", lambda self: [{"id": 1, "name": "Test"}])
    # Patch CSVSchemaGenerator to do nothing
    monkeypatch.setattr("src.pipeline.CSVSchemaGenerator", lambda *a, **kw: None)
    # Patch export_to_csv to just check data
    exported = {}
    def fake_export(self, data, path):
        exported["data"] = data
        exported["path"] = path
    monkeypatch.setattr("src.pipeline.DataPipeline.export_to_csv", fake_export)
    # Run pipeline
    pipeline = DataPipeline("dummy_path")
    pipeline.run()
    assert exported["data"] == [{"id": 1, "name": "Test"}]
    assert os.path.basename(exported["path"]) == "test_output.csv"