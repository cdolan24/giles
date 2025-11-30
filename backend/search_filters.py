"""
Advanced Search Filters for library queries
"""
from typing import Dict, Any

def apply_filters(query_params: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
    # Merge filters into query params
    for key, value in filters.items():
        if value is not None:
            query_params[key] = value
    return query_params

# Example usage:
# filters = {"author": "Doe", "year": 2020, "open_access": True}
# params = apply_filters({"q": "Quantum Computing"}, filters)
