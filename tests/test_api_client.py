import pytest
from unittest.mock import patch
from src.api_client import APIClient

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