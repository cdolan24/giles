"""
Ranking Engine for sorting papers/books by citations, ratings, references
"""
from typing import List, Dict

def rank_items(items: List[Dict], key: str = 'citation_count', reverse: bool = True) -> List[Dict]:
    return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)

# Example usage:
# papers = [{"title": "A", "citation_count": 10}, {"title": "B", "citation_count": 20}]
# ranked = rank_items(papers)
