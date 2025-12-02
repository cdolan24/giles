"""
Master Test Runner for UC Library Web-Scraper Backend
Runs all unit and integration tests to verify backend functionality before deployment.
"""
import unittest
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

test_modules = [
    'test_api_client',
    'test_backend',
    'test_citation_manager',
    'test_entity_linker',
    'test_prerequisite_recommender',
    'test_ranking_engine',
    'test_search_filters',
    'test_source_citation_tool',
    'test_summarizer',
]

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
        except Exception as e:
            print(f"Error loading {module_name}: {e}")
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    loader = unittest.TestLoader()
    suite = load_tests(loader, None, None)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
