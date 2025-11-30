"""
FastAPI backend server for UC Library Web-Scraper Extension
"""

from fastapi import FastAPI, Query
from typing import List, Dict, Any, Optional
from api_client import LibraryAPIClient, MCPResource
from search_filters import apply_filters
import uvicorn

app = FastAPI()

# Example: Load resources from config (hardcoded for now)
resources = [
    MCPResource(name="UC Library", base_url="https://uclibrary.example.edu/api", api_key="<your-api-key>")
]
client = LibraryAPIClient(resources)

@app.get("/search")
def search_papers(
    q: str = Query(..., description="Query string"),
    library: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    journal: Optional[str] = None,
    open_access: Optional[bool] = None,
    citation_count: Optional[int] = None
) -> List[Dict[str, Any]]:
    filters = {
        "author": author,
        "year": year,
        "journal": journal,
        "open_access": open_access,
        "citation_count": citation_count
    }
    params = apply_filters({"q": q}, filters)
    return client.search_papers(params["q"], library)

@app.get("/metadata/{paper_id}")
def get_metadata(paper_id: str, library: str) -> Dict[str, Any]:
    return client.get_metadata(paper_id, library)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
