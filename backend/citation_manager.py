"""
Citation Manager for tracking and formatting sources
"""
from typing import List, Dict, Any

class CitationManager:
    def __init__(self):
        self.citations = []

    def add_citation(self, citation: Dict[str, Any]):
        self.citations.append(citation)

    def get_citations(self) -> List[Dict[str, Any]]:
        return self.citations

    def format_citations(self) -> str:
        return '\n'.join([
            f"{c['author']} ({c['year']}), {c['title']}, {c['journal']}" for c in self.citations
            if all(k in c for k in ('author', 'year', 'title', 'journal'))
        ])

# Example usage:
# cm = CitationManager()
# cm.add_citation({"author": "Doe", "year": 2020, "title": "Quantum Computing", "journal": "Science"})
# print(cm.format_citations())
