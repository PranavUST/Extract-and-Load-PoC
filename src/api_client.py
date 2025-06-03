import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        logger.debug("APIClient initialized with config: %s", config)

    def _handle_pagination(self, params: Dict) -> List[Dict]:
        pagination = self.config.get('pagination', {})
        all_records = []
        max_pages = pagination.get('max_pages', 1)
        logger.info("Starting paginated fetch: max_pages=%d", max_pages)
        
        for page in range(1, max_pages + 1):
            params.update({
                pagination['page_param']: page,
                pagination['page_size_param']: pagination['page_size']
            })
            logger.debug("Requesting page %d with params: %s", page, params)
            response = self._make_request(params)
            records = self._extract_records(response)
            logger.info("Fetched %d records from page %d", len(records), page)
            if not records:
                logger.info("No more records found at page %d. Stopping pagination.", page)
                break
            all_records.extend(records)
            
        logger.info("Total records fetched: %d", len(all_records))
        return all_records

    def _make_request(self, params: Dict) -> Dict:
        try:
            resp = self.session.request(
                method=self.config['method'],
                url=self.config['url'],
                headers=self.config['headers'],
                params=params,
                timeout=self.config['timeout']
            )
            resp.raise_for_status()
            logger.debug("Request successful: %s %s", self.config['method'], self.config['url'])
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s", str(e))
            raise

    def _extract_records(self, response: Dict) -> List[Dict]:
        current_data = response
        for key in self.config['data_path'].split('.'):
            current_data = current_data.get(key, [])
        if isinstance(current_data, list):
            logger.debug("Extracted %d records from response", len(current_data))
            return current_data
        else:
            logger.warning("Data path did not yield a list. Got: %s", type(current_data))
            return []

    def fetch_data(self) -> List[Dict]:
        logger.info("Fetching data using APIClient")
        params = self.config.get('params', {})
        data = self._handle_pagination(params)
        logger.info("Data fetch complete. Total records: %d", len(data))
        return data
