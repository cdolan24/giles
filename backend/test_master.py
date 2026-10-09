"""
Master Test Runner for UC Library Web-Scraper Backend
Runs all unit and integration tests to verify backend functionality before deployment.
"""
import unittest
import os
import sys

# Add backend directory (bare module imports) and project root (backend.* imports) to path
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.dirname(BACKEND_DIR))

test_modules = [
    'test_api_client',
    'test_backend',
    'test_database',
    'test_citation_manager',
    'test_entity_linker',
    'test_prerequisite_recommender',
    'test_ranking_engine',
    'test_search_filters',
    'test_sources',
    'test_source_citation_tool',
    'test_summarizer',
]

load_errors = []

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
        except Exception as e:
            print(f"Error loading {module_name}: {e}")
            load_errors.append(module_name)
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    loader = unittest.TestLoader()
    suite = load_tests(loader, None, None)
    result = runner.run(suite)
    if load_errors:
        print(f"Failed to load test modules: {', '.join(load_errors)}")
    if not result.wasSuccessful() or load_errors:
        sys.exit(1)
