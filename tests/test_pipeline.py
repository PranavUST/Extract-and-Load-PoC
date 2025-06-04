import pytest
from unittest.mock import patch, MagicMock
from src.pipeline import DataPipeline

@patch('src.pipeline.APIClient')
@patch('src.pipeline.CSVSchemaGenerator')
@patch('src.pipeline.load_csv_to_db')
def test_pipeline_run(mock_load_csv, mock_schema_gen, mock_api_client, tmp_path):
    # Setup mocks
    mock_api_client.return_value.fetch_data.return_value = [{'id': 1, 'name': 'Test'}]
    mock_schema_gen.return_value.create_table_from_csv.return_value = None
    mock_load_csv.return_value = None

    # Minimal config
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
destination:
  csv:
    output_path: test.csv
    write_mode: overwrite
  database:
    enabled: false
    table: api_data
    auto_create_table: true
    handle_conflicts: true
    primary_key: id
source:
  api:
    url: ""
    method: GET
    headers: {}
    timeout: 10
    data_path: data.items
    pagination:
      max_pages: 1
      page_param: page
      page_size_param: limit
      page_size: 1
""")
    pipeline = DataPipeline(str(config_path))
    pipeline.run()