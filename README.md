
# Giles: UC Library Web-Scraper Agent

---
**Status:** Working prototype. Live search works end to end against arXiv. UC Library access is wired but disabled until a real endpoint and API key are configured (see [Configuration](#configuration)). User data is stored in a database (SQLite by default).

## Features
- Modular FastAPI backend with MCP resource wrappers for libraries
- Library sources loaded from config; each can have a backup web scraper that is used automatically if its API fails (arXiv: official API, with an HTML scraper as backup)
- React frontend chat widget and filters, displays backend search results and errors
- Browser extension popup for chat and search
- Citation management and export (Zotero, EndNote, BibTeX)
- Prerequisite recommender and ranking engine
- Entity linker for cross-source aggregation
- Multi-language support: not yet implemented
- Accessibility features
- User accounts, bookmarks, saved searches, sharing and notifications, stored in a database (see [Database](#database))
- Usage analytics from logged searches, and recommendations that re-run your saved and recent searches
- Usage analytics dashboard
- Unit tests for backend modules (`python backend/test_master.py`)

## Quickstart

### Backend (API server)
1. Install dependencies:
	```
	pip install -r backend/requirements.txt
	```
2. Run the backend server from the project root:
	```
	python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
	```
   Or use Docker for production (see `deployment/docker_backend_plan.md`).
3. Search is served at `GET /search?q=...` (optional: `library`, `author`, `year`, `journal`, `open_access`, `citation_count`). With no `library`, all enabled sources are searched. If a source's API fails, its backup scraper is used.

### Frontend (React app)
1. Install dependencies:
	```
	cd frontend
	npm install
	```
2. Start the frontend app:
	```
	npm start
	```
3. The chat widget displays backend search results, including fallback scraper results and error codes/messages if no results are found.

### Extension
1. Load the `extension` folder as an unpacked extension in your browser.
2. The extension connects to the backend API and provides a chat/search interface.


## Deployment
- See `deployment/docker_backend_plan.md` and `deployment/run_backend_production.md` for containerization and production setup.
- Use environment variables for secrets (see `deployment/env_vars_and_secrets.md`).

---
**Note:** Tabbed launching in Windows Terminal is still a to-do. The current script launches backend and frontend in separate windows for reliability. If you want tabbed launching, revisit this after further testing or Windows Terminal updates.

**Troubleshooting:**
- If the backend is running but not responding to frontend/API requests, check:
	- The backend logs for error codes (see recent error handling additions)
	- That your MCPResource and web scraper are correctly configured and reachable
	- That your config uses a valid endpoint or the web scraper selectors match the actual HTML structure
- If the frontend displays "No results found" or an error code, verify the backend `/search` endpoint and scraper configuration.

## Configuration
Library sources are read from `backend/config.json` if it exists, otherwise `backend/config.example.json` (override with `GILES_CONFIG`). Copy the example to `config.json` for local changes; `config.json` is git-ignored. Schema: `backend/config.schema.json`.

Each library has a `type` (`rest` for a generic JSON API returning `{"results": [...]}`, or `arxiv`), a `baseUrl`, an optional `apiKeyEnv` naming the environment variable that holds its key (sent as `Authorization: Bearer <key>`), `enabled`, and an optional `backupScraper` (`arxiv_scraper`, `uc_library_scraper`).

### Environment variables
| Variable | Purpose |
| --- | --- |
| `API_KEY_UC_LIBRARY` | UC Library API key |
| `DB_URL` | SQLAlchemy database URL. Default: SQLite file at `data/giles.db` |
| `SECRET_KEY` | JWT signing key. If unset, a random key is generated per run and logins don't survive restarts |
| `EXTERNAL_API_KEY` | Key for `/external_api`. If unset, that endpoint is disabled |
| `CORS_ORIGINS` | Comma-separated allowed browser origins (default: `http://localhost:3000`) |
| `DEBUG` | `true` for debug-level logging |
| `REACT_APP_API_URL` | Frontend: backend URL (default `http://127.0.0.1:8000`) |

### Enabling UC Library
The UC entry ships disabled because its URL is a placeholder. To enable it:
1. Get the real API endpoint and a key. UC Library Search runs on Ex Libris Primo, whose API keys are normally issued to institutions through a campus library's systems staff.
2. Set `baseUrl` in `config.json` and `API_KEY_UC_LIBRARY` in the environment, then set `enabled: true`.
3. If the API's response is not shaped `{"results": [...]}` with `title`/`author`/`year` fields, add a resource type for it (see `backend/arxiv_resource.py` for an example).
4. The UC backup scraper's URL and selectors (`backend/uc_library_scraper.py`) are placeholders and must be updated against the real search pages.

## Database
Tables are created automatically on startup (`backend/models.py`). By default the backend uses a SQLite file at `data/giles.db` (git-ignored). Set `DB_URL` to use another database, e.g. `postgresql+psycopg://user:pass@host/giles` (install the matching driver). In Docker, mount a volume at `/app/data` or the SQLite file is lost when the container is replaced.

Schema changes are not migrated automatically: `create_all` only creates missing tables. Delete `data/giles.db` in development, or add Alembic before changing tables in a deployment with real data.

### User endpoints
All except `/register` and `/token` need `Authorization: Bearer <token>`.

| Endpoint | Purpose |
| --- | --- |
| `POST /register` | JSON `{username, email, password}` (password 8–72 bytes) |
| `POST /token` | Form `username`, `password`; returns a bearer token (30 min) |
| `GET /profile` | Account info and counts |
| `GET/POST /bookmarks`, `DELETE /bookmarks/{id}` | Bookmarks. POST accepts a `/search` result as-is; duplicate URLs return the existing bookmark |
| `GET/POST /saved_searches`, `DELETE /saved_searches/{id}` | Saved queries with optional filters |
| `POST /share` | JSON `{peer_username, item}`; adds the paper to the peer's bookmarks and notifies them |
| `GET /notifications?unread_only=`, `POST /notifications/{id}/read` | Notifications |
| `GET /recommendations` | Results from your 3 most recent saved/recent searches, excluding bookmarked papers |
| `GET /analytics` | Your activity, top queries (30 days), search latency and no-result rate (24 hours) |
| `POST /export_citations?format=` | Bookmarks as `bibtex`, `zotero` or `endnote` |

`/search` works without a token; with one, the search is attributed to you in analytics.

## Documentation
- See `expanded_implementation_plan.md` for implementation details.
- See `product_philosophy.md` for design philosophy and user stories.
- See `session_logs/session_log.md` for progress logs.

---
For questions or further development, refer to the handoff document and session log.
