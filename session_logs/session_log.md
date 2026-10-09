# Giles Project Debugging & Update Log (Dec 4, 2025)

## What was fixed today

### Backend
- Confirmed FastAPI backend is running and `/search` endpoint is present in `/docs`.
- Discovered backend endpoints are served under `/api/search` (not `/search`).
- Ensured all backend error responses include an `error_code` field for consistent frontend error handling.
- Verified backend startup command and correct app module loading.

### Frontend
- Updated `frontend/src/api.js` to use `/api/search` instead of `/search`.
- Updated `frontend/src/ChatWidget.js` to display backend error messages and error codes to the user.
- Verified error codes propagate from backend to frontend and are displayed in the UI.

### DevOps & Scripts
- Fixed `start_all.ps1` to start backend from project root using uvicorn and correct PYTHONPATH, removed unnecessary `cd backend`.

### Testing & Debugging
- Used curl and browser to verify endpoint availability and error propagation.
- Confirmed `/search` endpoint is present in FastAPI docs and responds as expected.
- Validated health endpoint and OpenAPI spec.

## Next Steps
- Monitor for further errors and collect feedback.
- Continue updating documentation for new features and fixes.

---

# Update Log (Oct 5, 2026)

## Fixed
- Search returned `NO_RESULTS` for every query: `/search` defaulted `library` to `"default_library"`, which matched no source. It now searches all enabled sources.
- Frontend called `/api/search` (404); it now calls `/search`, which is what the backend serves. Added CORS so the React app's requests aren't blocked.
- Backend resources were hardcoded to a jsonplaceholder test URL. They now load from config, with API keys from environment variables.
- `config.example.json` was invalid JSON (comment). Fixed.
- Backup scraper fallback was documented but never wired. `LibraryAPIClient` now falls back to each source's scraper when its API fails.
- arXiv now uses the official API (`arxiv_resource.py`), with the HTML scraper as backup. Scrapers have timeouts and tolerate missing fields.
- Search filters were accepted but ignored; they now filter results. Unchecked "Open Access" no longer excludes open-access papers.
- `SECRET_KEY` and the external API key now come from env vars instead of hardcoded values.
- Test runner silently skipped two modules on import errors and still reported OK. Fixed, and failures to load now fail the run. Added `test_sources.py`.
- Extension popup escaped user input, shows results as links, and has host permission for the local backend.
- Added `.gitignore`; untracked `node_modules`, `frontend/build`, `__pycache__`, and logs.

# Update Log (Oct 5, 2026) — Database

- Added SQLAlchemy persistence (`backend/database.py`, `backend/models.py`): users, bookmarks, saved searches, notifications, and a search log. SQLite at `data/giles.db` by default; `DB_URL` overrides.
- Registration was crashing (passlib had no bcrypt backend; passlib is unmaintained). Replaced with the `bcrypt` library directly.
- `/register` now takes a JSON body instead of query parameters, so passwords no longer appear in URLs and server logs.
- `/profile` no longer returns the password hash.
- Replaced demo data: `/analytics` reports from the search log, `/notifications` are created by shares, `/recommendations` re-runs saved/recent searches, `/export_citations` reads bookmarks.
- New endpoints: bookmarks and saved searches (CRUD), mark notification read.
- `/search` logs each request (optionally attributed to the logged-in user).
- Dropped the unused `progress` field from users.
- Added `test_database.py` (14 tests; 35 total).
