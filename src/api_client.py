import requests
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class APIClient:
    """Client for fetching data from a REST API with pagination support."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        logger.debug("APIClient initialized with config: %s", config)

    def _handle_pagination(self, params: Dict) -> List[Dict]:
        pagination = self.config.get('pagination', {})
        all_records = []
        max_pages = pagination.get('max_pages', 1)
        page_param = pagination.get('page_param')
        page_size_param = pagination.get('page_size_param')
        page_size = pagination.get('page_size')
        logger.info("Starting paginated fetch: max_pages=%d", max_pages)

        if not (page_param and page_size_param and page_size):
            logger.warning("Pagination parameters missing, fetching only first page.")
            response = self._make_request(params)
            return self._extract_records(response)

        for page in range(1, max_pages + 1):
            page_params = params.copy()
            page_params.update({
                page_param: page,
                page_size_param: page_size
            })
            logger.debug("Requesting page %d with params: %s", page, page_params)
            response = self._make_request(page_params)
            records = self._extract_records(response)
            logger.info("Fetched %d records from page %d", len(records), page)
            if not records:
                logger.info("No more records found at page %d. Stopping pagination.", page)
                break
            all_records.extend(records)

        logger.info("Total records fetched: %d", len(all_records))
        return all_records

    def _make_request(self, params: Dict) -> Dict:
        retries = self.config.get('retries', 3)  # Default to 3 retries if not set
        delay = 2  # seconds between retries
        for attempt in range(1, retries + 1):
            try:
                resp = self.session.request(
                    method=self.config.get('method', 'GET'),
                    url=self.config.get('url', ''),
                    headers=self.config.get('headers', {}),
                    params=params,
                    timeout=self.config.get('timeout', 30)
                )
                resp.raise_for_status()
                logger.debug("Request successful: %s %s", self.config.get('method', 'GET'), self.config.get('url', ''))
                return resp.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached. Raising exception.")
                    raise

    def _extract_records(self, response: Dict) -> List[Dict]:
        """Extracts records from the API response using the configured data path."""
        data_path = self.config.get('data_path', '')
        current_data = response
        if data_path:
            for key in data_path.split('.'):
                if isinstance(current_data, dict):
                    current_data = current_data.get(key, [])
                else:
                    logger.warning("Data path did not yield a dict at key '%s'. Got: %s", key, type(current_data))
                    return []
        if isinstance(current_data, list):
            logger.debug("Extracted %d records from response", len(current_data))
            return current_data
        else:
            logger.warning("Data path did not yield a list. Got: %s", type(current_data))
            return []

    def fetch_data(self) -> List[Dict]:
        """Fetches data from the API using pagination."""
        logger.info("Fetching data using APIClient")
        params = self.config.get('params', {})
        data = self._handle_pagination(params)
        logger.info("Data fetch complete. Total records: %d", len(data))
        return data