"""
Prerequisite Recommender using graph-based relationships
"""
from typing import List, Dict

class PrerequisiteRecommender:
    def __init__(self, relationships: Dict[str, List[str]]):
        self.relationships = relationships

    def recommend(self, topic: str) -> List[str]:
        return self.relationships.get(topic, [])

# Example usage:
# relationships = {"Calculus": ["Algebra", "Trigonometry"], "Quantum Computing": ["Linear Algebra", "Calculus"]}
# pr = PrerequisiteRecommender(relationships)
# print(pr.recommend("Calculus"))
