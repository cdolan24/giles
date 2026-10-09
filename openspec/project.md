# Project Context

## Purpose
Giles is a research assistant that searches university and public scientific libraries (UC Library, arXiv, and later others) without duplicating their data. Each library is a pluggable source queried on demand. Users can search, bookmark papers, save searches, share papers with each other, and get recommendations based on their activity. Clients are a React chat widget and a browser extension popup.

See `product_philosophy.md` for user stories and `README.md` for setup.

## Tech Stack
- Backend: Python 3.13, FastAPI, Uvicorn
- Persistence: SQLAlchemy 2.x; SQLite by default (`data/giles.db`), any SQLAlchemy URL via `DB_URL`
- Auth: bcrypt password hashes, HS256 JWT bearer tokens (PyJWT)
- Sources: `requests` for HTTP APIs, BeautifulSoup for backup HTML scrapers, `xml.etree` for the arXiv Atom API
- Frontend: React (Create React App) in `frontend/`
- Extension: Manifest V3 popup in `extension/`

## Project Conventions

### Code Style
- Backend modules use package imports (`from backend.x import y`) and run from the project root (`python -m uvicorn backend.app:app`).
- Errors returned to clients carry an `error` message and a machine-readable `error_code`. `HTTPException` details use `{"error", "error_code"}`; `/search` returns errors as a one-element list with HTTP 200.
- Secrets and per-deployment settings come from environment variables, never source files.

### Architecture Patterns
- Each library is an `MCPResource` (`backend/mcp_resource.py`) built from config by `SourceManager` (`backend/source_manager.py`). Source types: `rest` (generic JSON API returning `{"results": [...]}`) and `arxiv`. New APIs get a new resource type rather than special cases in the client.
- Each resource may have a backup scraper; `LibraryAPIClient` falls back to it when the API fails.
- Filters are applied to fetched results (`backend/search_filters.py`) because most source APIs don't support them natively.
- Database access goes through the `get_db` FastAPI dependency so tests can override it.

### Testing Strategy
- `python backend/test_master.py` runs all backend tests (unittest). It fails if any test module fails to import.
- Tests must not hit the network: stub resources or patch `requests.get`.
- API tests use FastAPI's `TestClient` with `use_test_db()` from `backend/test_database.py` (in-memory SQLite per test).

### Git Workflow
- Feature branches off `main`; generated files (`node_modules`, `frontend/build`, `__pycache__`, `logs/`, `data/`) are ignored.
- `backend/config.json` and `.env` are local-only and ignored.

## Domain Context
- UC Library Search runs on Ex Libris Primo. Primo API keys are issued to institutions through a campus library's systems staff, not to individuals.
- arXiv provides a free, unauthenticated Atom API (`export.arxiv.org/api/query`); arXiv asks clients to prefer it over HTML scraping.
- arXiv has no citation counts; citation data would come from Semantic Scholar or Crossref.

## Important Constraints
- Don't store or mirror library content; fetch on demand and store only user data (bookmarks hold citation metadata and a link).
- bcrypt only hashes the first 72 bytes of a password, so longer passwords are rejected rather than silently truncated.
- No schema migrations yet: `create_all` only creates missing tables. Add Alembic before changing tables in a deployment with real data.

## External Dependencies
- arXiv API: https://info.arxiv.org/help/api/user-manual.html
- UC Library Search / Ex Libris Primo API: access requested, pending (see `changes/add-uc-library-source`)
