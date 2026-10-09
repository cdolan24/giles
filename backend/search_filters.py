"""
Advanced Search Filters for library queries
"""
from typing import Dict, Any, List


def apply_filters(query_params: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
    # Merge filters into query params
    for key, value in filters.items():
        if value is not None:
            query_params[key] = value
    return query_params


def filter_results(results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply filters to fetched results, for sources whose APIs don't support them natively.
    A result missing a filtered field is excluded."""
    author = (filters.get("author") or "").lower()
    journal = (filters.get("journal") or "").lower()
    year = filters.get("year")
    open_access = filters.get("open_access")
    min_citations = filters.get("citation_count")

    def keep(r):
        if author and author not in str(r.get("author", "")).lower():
            return False
        if journal and journal not in str(r.get("journal", "")).lower():
            return False
        if year is not None and r.get("year") != year:
            return False
        if open_access is not None and r.get("open_access") != open_access:
            return False
        if min_citations is not None and (r.get("citation_count") or 0) < min_citations:
            return False
        return True

    return [r for r in results if keep(r)]

# Example usage:
# filters = {"author": "Doe", "year": 2020, "open_access": True}
# params = backend.search_filters.apply_filters({"q": "Quantum Computing"}, filters)
