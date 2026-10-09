"""
API Client for Library Metadata and Papers
"""
from typing import List, Dict, Any, Optional
from backend.mcp_resource import MCPResource
import logging


class LibraryAPIClient:
    def __init__(self, resources: List[MCPResource]):
        self.resources = resources

    def search_papers(self, query: str, library_name: Optional[str] = None) -> List[Dict[str, Any]]:
        logging.debug(f"Starting search_papers with query: {query}, library_name: {library_name}")
        results = []
        for resource in self.resources:
            if library_name and resource.name != library_name:
                continue
            papers = self._search_resource(resource, query)
            for paper in papers:
                paper.setdefault("source", resource.name)
            results.extend(papers)
        return results

    def _search_resource(self, resource: MCPResource, query: str) -> List[Dict[str, Any]]:
        try:
            response = resource.query("search", {"q": query})
            if isinstance(response, dict) and "error" not in response:
                return response.get("results", [])
            logging.warning(f"{resource.name} API failed: {response.get('details') if isinstance(response, dict) else response}")
        except Exception as e:
            logging.error(f"Error querying {resource.name}: {e}")
        backup = getattr(resource, "backup_scraper", None)
        if backup is None:
            return []
        try:
            logging.info(f"Falling back to backup scraper for {resource.name}")
            return backup.search(query)
        except Exception as e:
            logging.error(f"Backup scraper for {resource.name} failed: {e}")
            return []

    def get_metadata(self, paper_id: str, library_name: str) -> Dict[str, Any]:
        for resource in self.resources:
            if resource.name == library_name:
                try:
                    return resource.query(f"metadata/{paper_id}")
                except Exception as e:
                    logging.error(f"Error fetching metadata from {library_name}: {e}")
        return {}

# Example usage:
# resources = [MCPResource(...), ...]
# client = LibraryAPIClient(resources)
# papers = client.search_papers("Quantum Computing")
# metadata = client.get_metadata("paper123", "UC Library")
