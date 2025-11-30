import unittest
from api_client import LibraryAPIClient, MCPResource

class DummyResource(MCPResource):
    def query(self, endpoint, params=None):
        if endpoint == "search":
            return {"results": [{"id": "1", "title": "Quantum Computing Paper", "author": "Doe", "year": 2020, "journal": "Science"}]}
        if endpoint.startswith("metadata/"):
            return {"id": endpoint.split("/")[1], "title": "Quantum Computing Paper", "author": "Doe"}
        return {}

class TestLibraryAPIClient(unittest.TestCase):
    def setUp(self):
        self.resource = DummyResource(name="UC Library", base_url="http://dummy")
        self.client = LibraryAPIClient([self.resource])

    def test_search_papers(self):
        results = self.client.search_papers("Quantum Computing")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Quantum Computing Paper")

    def test_get_metadata(self):
        metadata = self.client.get_metadata("1", "UC Library")
        self.assertEqual(metadata["id"], "1")
        self.assertEqual(metadata["author"], "Doe")

if __name__ == "__main__":
    unittest.main()
