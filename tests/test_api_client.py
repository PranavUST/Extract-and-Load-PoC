import pytest
from unittest.mock import patch, MagicMock
from api_client import APIClient

def test_fetch_data_pagination():
    config = {
        'method': 'GET',
        'url': 'http://test.com',
        'headers': {},
        'timeout': 30,
        'pagination': {'max_pages': 2, 'page_param': 'page', 'page_size_param': 'limit', 'page_size': 1},
        'data_path': 'data.items'
    }
    # Mock response data for two pages
    page1 = {'data': {'items': [{'id': 1}]}}
    page2 = {'data': {'items': []}}
    with patch.object(APIClient, '_make_request', side_effect=[page1, page2]):
        client = APIClient(config)
        data = client.fetch_data()
        assert data == [{'id': 1}]

def test_handle_pagination_no_pagination_params():
    config = {
        'method': 'GET',
        'url': 'http://test.com',
        'headers': {},
        'timeout': 30,
        'data_path': 'data.items'
    }
    response = {'data': {'items': [{'id': 1}, {'id': 2}]}}
    with patch.object(APIClient, '_make_request', return_value=response):
        client = APIClient(config)
        result = client._handle_pagination({})
        assert result == [{'id': 1}, {'id': 2}]

def test_handle_pagination_with_empty_pages():
    config = {
        'method': 'GET',
        'url': 'http://test.com',
        'headers': {},
        'timeout': 30,
        'pagination': {'max_pages': 3, 'page_param': 'page', 'page_size_param': 'limit', 'page_size': 1},
        'data_path': 'data.items'
    }
    # First page has data, second is empty
    page1 = {'data': {'items': [{'id': 1}]}}
    page2 = {'data': {'items': []}}
    with patch.object(APIClient, '_make_request', side_effect=[page1, page2]):
        client = APIClient(config)
        result = client._handle_pagination({})
        assert result == [{'id': 1}]

def test_make_request_success(monkeypatch):
    config = {
        'method': 'GET',
        'url': 'http://test.com',
        'headers': {},
        'timeout': 30
    }
    mock_response = MagicMock()
    mock_response.json.return_value = {'result': 'ok'}
    mock_response.raise_for_status.return_value = None

    class MockSession:
        def request(self, **kwargs):
            return mock_response

    client = APIClient(config)
    client.session = MockSession()
    result = client._make_request({})
    assert result == {'result': 'ok'}

def test_extract_records_with_valid_path():
    config = {'data_path': 'data.items'}
    client = APIClient(config)
    response = {'data': {'items': [{'id': 1}, {'id': 2}]}}
    records = client._extract_records(response)
    assert records == [{'id': 1}, {'id': 2}]

def test_extract_records_with_invalid_path():
    config = {'data_path': 'data.missing'}
    client = APIClient(config)
    response = {'data': {'items': [{'id': 1}]}}
    records = client._extract_records(response)
    assert records == []

def test_extract_records_path_not_list():
    config = {'data_path': 'data'}
    client = APIClient(config)
    response = {'data': {'items': [{'id': 1}]}}
    records = client._extract_records(response)
    assert records == []

def test_extract_records_no_path():
    config = {}
    client = APIClient(config)
    response = [{'id': 1}]
    records = client._extract_records(response)
    assert records == [{'id': 1}]

def test_extract_records_path_midway_not_dict():
    config = {'data_path': 'data.items'}
    client = APIClient(config)
    response = {'data': 123}  # 'data' is not a dict, so .get('items') will fail
    records = client._extract_records(response)
    assert records == []