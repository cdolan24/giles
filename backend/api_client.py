"""
API Client for Library Metadata and Papers
"""
from typing import List, Dict, Any
from mcp_resource import MCPResource

class LibraryAPIClient:
    def __init__(self, resources: List[MCPResource]):
        self.resources = resources

    def search_papers(self, query: str, library_name: str = None) -> List[Dict[str, Any]]:
        results = []
        for resource in self.resources:
            if library_name and resource.name != library_name:
                continue
            try:
                papers = resource.query("search", {"q": query})
                results.extend(papers.get("results", []))
            except Exception as e:
                print(f"Error querying {resource.name}: {e}")
                # Try backup scraper if available
                backup_scraper_name = getattr(resource, 'backup_scraper', None)
                if backup_scraper_name:
                    try:
                        # Dynamically import and use the backup scraper
                        import importlib
                        scraper_module = importlib.import_module(backup_scraper_name)
                        ScraperClass = getattr(scraper_module, backup_scraper_name.split('_')[0].capitalize() + 'Scraper')
                        scraper = ScraperClass()
                        scraped_results = scraper.search(query)
                        print(f"Used backup scraper {backup_scraper_name} for {resource.name}")
                        results.extend(scraped_results)
                    except Exception as se:
                        print(f"ERROR_CODE:SCRAPER_FAIL | {type(se).__name__}: {se}")
        return results

    def get_metadata(self, paper_id: str, library_name: str) -> Dict[str, Any]:
        for resource in self.resources:
            if resource.name == library_name:
                try:
                    return resource.query(f"metadata/{paper_id}")
                except Exception as e:
                    print(f"Error fetching metadata from {library_name}: {e}")
        return {}

# Example usage:
# resources = [MCPResource(...), ...]
# client = LibraryAPIClient(resources)
# papers = client.search_papers("Quantum Computing")
# metadata = client.get_metadata("paper123", "UC Library")
