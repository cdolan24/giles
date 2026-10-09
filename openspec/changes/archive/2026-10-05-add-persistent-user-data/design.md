## Context
Session of 2026-10-05, after the search pipeline fix. The user asked for the database, which was next step #2 in the evaluation. At the same time they requested UC Library (Primo) API access.

### Findings
- `POST /register` raised `passlib.exc.MissingBackendError: bcrypt: no backends available`. passlib 1.7.4 is unmaintained and also breaks with bcrypt ≥ 4.1.
- `GET /profile` returned the whole user model, including `hashed_password`.
- `/register` took the password as a query parameter, so it would appear in access logs.
- Neither the frontend nor the extension called any auth endpoint, so request shapes could change without breaking clients.
- Every authenticated endpoint repeated the same JWT decode block.

## Goals / Non-Goals
- Goals: persistent accounts and user data; replace every demo response that a database can make real; keep tests offline and fast.
- Non-Goals: migrations, account UI in the clients, real Zotero/EndNote formats, ML-based recommendations.

## Decisions
- **SQLAlchemy 2.x with SQLite by default.** No server to run locally, and `DB_URL` switches to Postgres for deployment. The stdlib `sqlite3` module would have locked the project to SQLite.
- **`create_all` on startup via FastAPI lifespan, no Alembic yet.** Acceptable while there is no production data; noted as a constraint in `project.md`.
- **`get_db` dependency plus `get_current_user` / `get_optional_user`.** This removes the duplicated JWT handling, and tests can swap the database with `dependency_overrides`.
- **Bookmarks store citation metadata columns, not the whole result.** This is enough for display and export, and keeps the rule against mirroring library content. Deduplicated by URL per user.
- **Sharing writes a bookmark plus a notification** instead of a separate shares table. A share is "someone put this on your list", and `shared_by` preserves who did it.
- **Search log drives analytics and recommendations.** One table answers engagement, popular topics, latency and no-result rate.
- **Recommendations re-run recent queries.** Saved searches come first, then logged searches; 3 queries, 10 results, bookmarked papers excluded. Simple and explainable (`based_on`); ranking can come later.
- **Portable SQL.** Used `CASE` instead of SQLite's `iif` for the no-result count, so the analytics query also works on Postgres.

## Risks / Trade-offs
- Recommendations make live source requests (up to 3 searches) → slower endpoint; acceptable at current scale, could cache later.
- Notifications are capped at 50 in responses but never pruned in storage.
- The `/search` log stores raw query text, including anonymous queries → consider retention limits before a public deployment.

## Verification
- `python backend/test_master.py`: 35 tests (14 new in `test_database.py`), all passing, each on an in-memory SQLite database.
- Two separate server processes on one SQLite file: register, search, bookmark and saved search in the first; in the second, profile showed 1 bookmark and 1 saved search, analytics showed the search (2063 ms), and recommendations returned 9 of 10 results (the bookmarked paper was excluded).
- Tests didn't create `data/giles.db`.

## Follow-ups
- Account UI in the React app and extension → `changes/add-account-ui`
- Alembic before the first schema change in a deployment with data
- Search-log retention policy
