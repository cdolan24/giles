import unittest
from citation_manager import CitationManager

class TestCitationManager(unittest.TestCase):
    def test_add_and_format_citations(self):
        cm = CitationManager()
        cm.add_citation({"author": "Doe", "year": 2020, "title": "Quantum Computing", "journal": "Science"})
        cm.add_citation({"author": "Smith", "year": 2021, "title": "AI", "journal": "Nature"})
        formatted = cm.format_citations()
        self.assertIn("Doe (2020), Quantum Computing, Science", formatted)
        self.assertIn("Smith (2021), AI, Nature", formatted)
        self.assertEqual(len(cm.get_citations()), 2)

if __name__ == "__main__":
    unittest.main()
