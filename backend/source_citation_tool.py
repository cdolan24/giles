"""
Source Citation Tool for formatting and attaching sources
"""
from typing import Dict

def format_citation(source: Dict) -> str:
    author = source.get('author', 'Unknown')
    year = source.get('year', 'N/A')
    title = source.get('title', 'Untitled')
    journal = source.get('journal', 'N/A')
    return f"{author} ({year}), {title}, {journal}"

# Example usage:
# source = {"author": "Doe", "year": 2020, "title": "Quantum Computing", "journal": "Science"}
# print(format_citation(source))
