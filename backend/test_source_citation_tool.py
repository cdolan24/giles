import unittest
from source_citation_tool import format_citation

class TestSourceCitationTool(unittest.TestCase):
    def test_format_citation(self):
        source = {
            "author": "Doe",
            "year": 2020,
            "title": "Quantum Computing",
            "journal": "Science"
        }
        citation = format_citation(source)
        self.assertEqual(citation, "Doe (2020), Quantum Computing, Science")

    def test_missing_fields(self):
        source = {"title": "Quantum Computing"}
        citation = format_citation(source)
        self.assertIn("Unknown", citation)
        self.assertIn("Quantum Computing", citation)

if __name__ == "__main__":
    unittest.main()
