import json
import os
import tempfile
import unittest
from unittest import mock
from backend.api_client import LibraryAPIClient
from backend.mcp_resource import MCPResource
from backend.arxiv_resource import ArxivResource, parse_feed
from backend.search_filters import filter_results
from backend.source_manager import SourceManager

ATOM_SAMPLE = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2211.02350v1</id>
    <published>2022-11-04T10:14:47Z</published>
    <title>Tierkreis: A Dataflow
      Framework</title>
    <summary>We present Tierkreis.</summary>
    <author><name>Seyon Sivarajah</name></author>
    <author><name>Lukas Heidemann</name></author>
  </entry>
</feed>"""


class FailingResource(MCPResource):
    def query(self, endpoint, params=None):
        return {"error": "QUERY_FAIL", "details": "down"}


class StubScraper:
    def search(self, query):
        return [{"title": f"Scraped {query}"}]


class TestFallback(unittest.TestCase):
    def test_backup_scraper_used_when_api_fails(self):
        resource = FailingResource("UC Library", "http://dummy", backup_scraper=StubScraper())
        results = LibraryAPIClient([resource]).search_papers("qubits")
        self.assertEqual(results, [{"title": "Scraped qubits", "source": "UC Library"}])

    def test_failure_without_scraper_returns_empty(self):
        resource = FailingResource("UC Library", "http://dummy")
        self.assertEqual(LibraryAPIClient([resource]).search_papers("qubits"), [])


class TestArxivResource(unittest.TestCase):
    def test_parse_feed(self):
        paper = parse_feed(ATOM_SAMPLE)[0]
        self.assertEqual(paper["id"], "2211.02350v1")
        self.assertEqual(paper["title"], "Tierkreis: A Dataflow Framework")
        self.assertEqual(paper["author"], "Seyon Sivarajah, Lukas Heidemann")
        self.assertEqual(paper["year"], 2022)
        self.assertTrue(paper["open_access"])

    def test_search_returns_results(self):
        response = mock.Mock(text=ATOM_SAMPLE, raise_for_status=lambda: None)
        with mock.patch("backend.arxiv_resource.requests.get", return_value=response):
            result = ArxivResource().query("search", {"q": "dataflow"})
        self.assertEqual(len(result["results"]), 1)


class TestSourceManager(unittest.TestCase):
    def write_config(self, libraries):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"libraries": libraries}, f)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_example_config_is_valid(self):
        SourceManager(os.path.join(os.path.dirname(__file__), "config.example.json"))

    def test_api_key_read_from_env_and_disabled_skipped(self):
        path = self.write_config([
            {"name": "UC Library", "baseUrl": "http://uc", "apiKeyEnv": "TEST_UC_KEY", "enabled": True,
             "backupScraper": "uc_library_scraper"},
            {"name": "Off", "baseUrl": "http://off", "enabled": False},
        ])
        with mock.patch.dict(os.environ, {"TEST_UC_KEY": "secret"}):
            resources = SourceManager(path).build_resources()
        self.assertEqual([r.name for r in resources], ["UC Library"])
        self.assertEqual(resources[0].api_key, "secret")
        self.assertIsNotNone(resources[0].backup_scraper)


class TestFilterResults(unittest.TestCase):
    def test_filters(self):
        results = [
            {"title": "A", "author": "Jane Doe", "year": 2020, "open_access": True},
            {"title": "B", "author": "John Roe", "year": 2021, "open_access": False},
        ]
        self.assertEqual([r["title"] for r in filter_results(results, {"author": "doe"})], ["A"])
        self.assertEqual([r["title"] for r in filter_results(results, {"year": 2021})], ["B"])
        self.assertEqual([r["title"] for r in filter_results(results, {"open_access": True})], ["A"])
        self.assertEqual(len(filter_results(results, {"author": None, "year": None})), 2)


class TestSearchEndpoint(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from backend import app as app_module
        from backend.test_database import use_test_db
        use_test_db(self)
        self.app_module = app_module
        self.http = TestClient(app_module.app)

    def test_search_all_libraries_by_default(self):
        stub = LibraryAPIClient([FailingResource("arXiv", "http://dummy", backup_scraper=StubScraper())])
        with mock.patch.object(self.app_module, "client", stub):
            body = self.http.get("/search", params={"q": "qubits"}).json()
        self.assertEqual(body[0]["title"], "Scraped qubits")

    def test_cors_allows_frontend(self):
        r = self.http.options("/search", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
        self.assertEqual(r.headers.get("access-control-allow-origin"), "http://localhost:3000")


if __name__ == "__main__":
    unittest.main()
