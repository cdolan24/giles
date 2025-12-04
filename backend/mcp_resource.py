"""
MCP Resource Wrappers for Supported Libraries
"""
from typing import Dict, Any
import requests
import logging

class MCPResource:
    def __init__(self, name: str, base_url: str, api_key: str = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key

    def query(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        logging.debug(f"Querying endpoint: {endpoint} with params: {params}")
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=headers)
            response.raise_for_status()
            logging.debug(f"Response from {self.base_url}/{endpoint}: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error querying {self.name} at endpoint '{endpoint}': {e}")
            return {"error": "QUERY_FAIL", "details": str(e)}

# Example usage:
# uc_resource = MCPResource(name="UC Library", base_url="https://uclibrary.example.edu/api", api_key="<your-api-key>")
# result = uc_resource.query("search", {"q": "Quantum Computing"})
