import unittest
from prerequisite_recommender import PrerequisiteRecommender

class TestPrerequisiteRecommender(unittest.TestCase):
    def test_recommend(self):
        relationships = {
            "Calculus": ["Algebra", "Trigonometry"],
            "Quantum Computing": ["Linear Algebra", "Calculus"]
        }
        pr = PrerequisiteRecommender(relationships)
        self.assertEqual(pr.recommend("Calculus"), ["Algebra", "Trigonometry"])
        self.assertEqual(pr.recommend("Quantum Computing"), ["Linear Algebra", "Calculus"])
        self.assertEqual(pr.recommend("Unknown"), [])

if __name__ == "__main__":
    unittest.main()
