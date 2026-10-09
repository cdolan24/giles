import datetime
import os
import tempfile
import unittest
from unittest import mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from backend import app as app_module
from backend.api_client import LibraryAPIClient
from backend.database import get_db, init_db, make_engine
from backend.models import SearchLog

PAPER = {"id": "2211.02350", "title": "Tierkreis", "author": "Sivarajah", "year": 2022,
         "journal": "arXiv", "url": "https://arxiv.org/abs/2211.02350", "source": "arXiv", "abstract": "ignored"}


def use_test_db(testcase, url="sqlite://"):
    """Point the app at a fresh database for the duration of a test."""
    engine = make_engine(url)
    init_db(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app_module.app.dependency_overrides[get_db] = override
    testcase.addCleanup(app_module.app.dependency_overrides.clear)
    testcase.addCleanup(engine.dispose)
    return Session


class StubResource:
    name = "arXiv"

    def __init__(self, papers):
        self.papers = papers

    def query(self, endpoint, params=None):
        return {"results": [dict(p) for p in self.papers]}


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.Session = use_test_db(self)
        self.http = TestClient(app_module.app)

    def register(self, username="alice", password="correct horse"):
        r = self.http.post("/register", json={"username": username, "email": f"{username}@example.edu", "password": password})
        self.assertEqual(r.status_code, 201, r.text)
        token = self.http.post("/token", data={"username": username, "password": password}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}


class TestAuth(DatabaseTestCase):
    def test_register_login_profile(self):
        auth = self.register()
        profile = self.http.get("/profile", headers=auth).json()
        self.assertEqual(profile["username"], "alice")
        self.assertNotIn("hashed_password", profile)

    def test_duplicate_username_rejected(self):
        self.register()
        r = self.http.post("/register", json={"username": "alice", "email": "a@b.c", "password": "another pass"})
        self.assertEqual(r.json()["detail"]["error_code"], "USERNAME_EXISTS")

    def test_wrong_password_rejected(self):
        self.register()
        r = self.http.post("/token", data={"username": "alice", "password": "wrong password"})
        self.assertEqual(r.status_code, 401)

    def test_overlong_password_rejected(self):
        r = self.http.post("/register", json={"username": "bob", "email": "b@x.y", "password": "x" * 73})
        self.assertEqual(r.json()["detail"]["error_code"], "PASSWORD_TOO_LONG")

    def test_users_persist_across_sessions(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            url = f"sqlite:///{os.path.join(tmp, 'sub', 'giles.db')}"
            use_test_db(self, url)
            self.register()
            app_module.app.dependency_overrides.clear()
            use_test_db(self, url)  # new engine on the same file
            r = self.http.post("/token", data={"username": "alice", "password": "correct horse"})
            self.assertEqual(r.status_code, 200)
            app_module.app.dependency_overrides.clear()


class TestBookmarks(DatabaseTestCase):
    def test_create_list_delete(self):
        auth = self.register()
        r = self.http.post("/bookmarks", json=PAPER, headers=auth)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["paper_id"], "2211.02350")
        self.assertEqual(self.http.post("/bookmarks", json=PAPER, headers=auth).status_code, 200)  # deduped by URL
        bookmarks = self.http.get("/bookmarks", headers=auth).json()["bookmarks"]
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(self.http.delete(f"/bookmarks/{bookmarks[0]['id']}", headers=auth).status_code, 204)
        self.assertEqual(self.http.get("/bookmarks", headers=auth).json()["bookmarks"], [])

    def test_cannot_delete_other_users_bookmark(self):
        alice = self.register("alice")
        bob = self.register("bob")
        bookmark_id = self.http.post("/bookmarks", json=PAPER, headers=alice).json()["id"]
        self.assertEqual(self.http.delete(f"/bookmarks/{bookmark_id}", headers=bob).status_code, 404)

    def test_export_bibtex_uses_bookmarks(self):
        auth = self.register()
        self.http.post("/bookmarks", json=PAPER, headers=auth)
        bibtex = self.http.post("/export_citations", params={"format": "bibtex"}, headers=auth).json()["bibtex"]
        self.assertIn("Tierkreis", bibtex)


class TestSavedSearches(DatabaseTestCase):
    def test_create_list_delete(self):
        auth = self.register()
        saved = self.http.post("/saved_searches", json={"query": "qubits", "filters": {"year": 2024}}, headers=auth).json()
        self.assertEqual(saved["filters"], {"year": 2024})
        self.assertEqual(len(self.http.get("/saved_searches", headers=auth).json()["saved_searches"]), 1)
        self.assertEqual(self.http.delete(f"/saved_searches/{saved['id']}", headers=auth).status_code, 204)


class TestSharing(DatabaseTestCase):
    def test_share_adds_bookmark_and_notification(self):
        alice = self.register("alice")
        bob = self.register("bob")
        r = self.http.post("/share", json={"peer_username": "bob", "item": PAPER}, headers=alice)
        self.assertEqual(r.status_code, 200, r.text)
        bookmark = self.http.get("/bookmarks", headers=bob).json()["bookmarks"][0]
        self.assertEqual(bookmark["shared_by"], "alice")
        notes = self.http.get("/notifications", headers=bob).json()["notifications"]
        self.assertEqual(len(notes), 1)
        self.assertIn("alice shared", notes[0]["msg"])
        self.http.post(f"/notifications/{notes[0]['id']}/read", headers=bob)
        self.assertEqual(self.http.get("/notifications", params={"unread_only": True}, headers=bob).json()["notifications"], [])

    def test_share_with_unknown_user(self):
        alice = self.register("alice")
        r = self.http.post("/share", json={"peer_username": "nobody", "item": PAPER}, headers=alice)
        self.assertEqual(r.status_code, 404)


class TestSearchLoggingAndAnalytics(DatabaseTestCase):
    def test_searches_logged_and_reported(self):
        auth = self.register()
        stub = LibraryAPIClient([StubResource([PAPER])])
        with mock.patch.object(app_module, "client", stub):
            self.http.get("/search", params={"q": "Qubits"}, headers=auth)
            self.http.get("/search", params={"q": "qubits"})  # anonymous
            self.http.get("/search", params={"q": "lasers", "year": 1999}, headers=auth)  # no results
        with self.Session() as db:
            self.assertEqual(db.query(SearchLog).count(), 3)
            self.assertEqual(db.query(SearchLog).filter(SearchLog.user_id.is_(None)).count(), 1)

        analytics = self.http.get("/analytics", headers=auth).json()["analytics"]
        self.assertEqual(analytics["engagement"]["searches"], 2)
        self.assertEqual(analytics["popular_topics"][0], {"query": "qubits", "count": 2})
        self.assertEqual(analytics["system_performance"]["searches_last_24h"], 3)
        self.assertAlmostEqual(analytics["system_performance"]["no_result_rate"], 0.333)

    def test_old_searches_excluded_from_popular_topics(self):
        auth = self.register()
        with self.Session() as db:
            db.add(SearchLog(query="ancient", result_count=1, duration_ms=5,
                             created_at=datetime.datetime(2020, 1, 1)))
            db.commit()
        analytics = self.http.get("/analytics", headers=auth).json()["analytics"]
        self.assertEqual(analytics["popular_topics"], [])


class TestRecommendations(DatabaseTestCase):
    def test_recommends_unbookmarked_results_from_saved_searches(self):
        auth = self.register()
        other = dict(PAPER, id="2401.00001", title="Other paper", url="https://arxiv.org/abs/2401.00001")
        self.http.post("/bookmarks", json=PAPER, headers=auth)
        self.http.post("/saved_searches", json={"query": "dataflow"}, headers=auth)
        stub = LibraryAPIClient([StubResource([PAPER, other])])
        with mock.patch.object(app_module, "client", stub):
            body = self.http.get("/recommendations", headers=auth).json()
        self.assertEqual(body["based_on"], ["dataflow"])
        self.assertEqual([p["title"] for p in body["recommendations"]], ["Other paper"])


if __name__ == "__main__":
    unittest.main()
