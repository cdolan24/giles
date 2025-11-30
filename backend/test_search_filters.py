import unittest
from search_filters import apply_filters

class TestSearchFilters(unittest.TestCase):
    def test_apply_filters(self):
        query_params = {"q": "Quantum Computing"}
        filters = {"author": "Doe", "year": 2020, "open_access": True}
        result = apply_filters(query_params, filters)
        self.assertEqual(result["author"], "Doe")
        self.assertEqual(result["year"], 2020)
        self.assertTrue(result["open_access"])
        self.assertEqual(result["q"], "Quantum Computing")

if __name__ == "__main__":
    unittest.main()
