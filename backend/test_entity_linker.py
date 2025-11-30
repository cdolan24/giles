import unittest
from entity_linker import link_entities

class TestEntityLinker(unittest.TestCase):
    def test_link_entities(self):
        contents = [
            {"title": "Quantum Computing", "author": "Doe"},
            {"title": "Quantum Computing", "author": "Smith"},
            {"title": "AI", "author": "Lee"}
        ]
        linked = link_entities(contents)
        titles = [c["title"] for c in linked]
        self.assertIn("Quantum Computing", titles)
        self.assertIn("AI", titles)
        self.assertEqual(len(linked), 2)

if __name__ == "__main__":
    unittest.main()
