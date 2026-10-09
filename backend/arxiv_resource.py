"""
arXiv resource backed by the official arXiv API (Atom feed).
https://info.arxiv.org/help/api/user-manual.html
"""
from typing import Dict, Any, List
import xml.etree.ElementTree as ET
import requests
import logging
from backend.mcp_resource import MCPResource, REQUEST_TIMEOUT

ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'


def parse_feed(xml_text: str) -> List[Dict[str, Any]]:
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall(f'{ATOM}entry'):
        def text(tag):
            el = entry.find(tag)
            return ' '.join(el.text.split()) if el is not None and el.text else ''
        authors = [a.findtext(f'{ATOM}name', '').strip() for a in entry.findall(f'{ATOM}author')]
        published = text(f'{ATOM}published')
        abs_url = text(f'{ATOM}id')
        papers.append({
            'id': abs_url.rsplit('/abs/', 1)[-1],
            'title': text(f'{ATOM}title'),
            'author': ', '.join(authors),
            'year': int(published[:4]) if published[:4].isdigit() else None,
            'journal': text(f'{ARXIV}journal_ref') or 'arXiv',
            'abstract': text(f'{ATOM}summary'),
            'url': abs_url,
            'open_access': True,
        })
    return papers


class ArxivResource(MCPResource):
    def __init__(self, name: str = "arXiv", base_url: str = "https://export.arxiv.org/api/query",
                 api_key: str = None, backup_scraper=None, max_results: int = 10):
        super().__init__(name, base_url, api_key, backup_scraper)
        self.max_results = max_results

    def query(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        params = params or {}
        if endpoint == "search":
            api_params = {'search_query': f"all:{params.get('q', '')}", 'max_results': self.max_results}
        elif endpoint.startswith("metadata/"):
            api_params = {'id_list': endpoint.split("/", 1)[1]}
        else:
            return {"error": "UNSUPPORTED_ENDPOINT", "details": endpoint}
        try:
            response = requests.get(self.base_url, params=api_params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            papers = parse_feed(response.text)
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            logging.error(f"Error querying {self.name}: {e}")
            return {"error": "QUERY_FAIL", "details": str(e)}
        if endpoint == "search":
            return {"results": papers}
        return papers[0] if papers else {}
