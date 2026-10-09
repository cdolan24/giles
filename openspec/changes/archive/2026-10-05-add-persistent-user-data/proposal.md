## Why
User accounts lived in an in-memory dict and were lost on every restart. Registration crashed outright because passlib had no bcrypt backend, and passlib is unmaintained. `/profile` returned the password hash. There was no way to add bookmarks or saved searches, so `/recommendations` and `/export_citations` only ever saw data created by `/share`. `/analytics` and `/notifications` returned hardcoded demo values.

## What Changes
- Add SQLAlchemy persistence (`backend/database.py`, `backend/models.py`): users, bookmarks, saved searches, notifications, search log. SQLite at `data/giles.db` by default; `DB_URL` overrides
- Hash passwords with `bcrypt` directly; reject passwords over 72 bytes
- **BREAKING**: `/register` takes a JSON body instead of query parameters (no client used it)
- **BREAKING**: `/share` takes a JSON body `{peer_username, item}`
- `/profile` returns account info and counts; no password hash
- New: bookmarks and saved searches (list, add, delete); `POST /notifications/{id}/read`
- `/share` creates a bookmark for the peer and a notification
- `/search` logs each request, attributed to the user when a token is sent
- `/analytics` and `/recommendations` computed from stored data
- Remove the unused `progress` field from users

## Impact
- Affected specs: `user-accounts`, `reading-list`, `usage-insights` (all new)
- Affected code: `backend/app.py`, `backend/database.py` (new), `backend/models.py` (new), `backend/test_database.py` (new), `backend/test_sources.py`, `backend/requirements.txt`, `.gitignore`, `README.md`
- Dependencies: `passlib` removed; `bcrypt` and `sqlalchemy>=2.0` added
- Deployments with Docker need a volume at `/app/data` for SQLite
