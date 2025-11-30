"""
Entity Linker for cross-source content aggregation
"""
from typing import List, Dict

def link_entities(contents: List[Dict]) -> List[Dict]:
    # Dummy implementation: group by title
    linked = {}
    for content in contents:
        title = content.get('title', '').lower()
        if title not in linked:
            linked[title] = content
    return list(linked.values())

# Example usage:
# papers = [{"title": "Quantum Computing"}, {"title": "Quantum Computing"}]
# linked = link_entities(papers)
