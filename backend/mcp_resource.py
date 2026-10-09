"""
MCP Resource Wrappers for Supported Libraries
"""
from typing import Dict, Any, Optional
import requests
import logging

REQUEST_TIMEOUT = 15


class MCPResource:
    def __init__(self, name: str, base_url: str, api_key: str = None, backup_scraper: Optional[Any] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.backup_scraper = backup_scraper

    def query(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        logging.debug(f"Querying endpoint: {endpoint} with params: {params}")
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            logging.error(f"Error querying {self.name} at endpoint '{endpoint}': {e}")
            return {"error": "QUERY_FAIL", "details": str(e)}

# Example usage:
# uc_resource = MCPResource(name="UC Library", base_url="https://uclibrary.example.edu/api", api_key="<your-api-key>")
# result = uc_resource.query("search", {"q": "Quantum Computing"})
