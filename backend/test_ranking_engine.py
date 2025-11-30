import unittest
from ranking_engine import rank_items

class TestRankingEngine(unittest.TestCase):
    def test_rank_items(self):
        items = [
            {"title": "A", "citation_count": 10},
            {"title": "B", "citation_count": 20},
            {"title": "C", "citation_count": 5}
        ]
        ranked = rank_items(items)
        self.assertEqual(ranked[0]["title"], "B")
        self.assertEqual(ranked[-1]["title"], "C")

if __name__ == "__main__":
    unittest.main()
