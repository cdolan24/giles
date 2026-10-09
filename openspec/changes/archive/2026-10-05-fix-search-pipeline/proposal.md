## Why
The project was marked "all features implemented and tested", but no search could return results. `/search` defaulted `library` to `"default_library"`, which matched no source, so every query returned `NO_RESULTS`. The frontend called `/api/search` (404), the backend sent no CORS headers, sources were hardcoded to a jsonplaceholder test URL, and the documented scraper fallback was never called. Two test modules failed to import, but the runner still reported success.

## What Changes
- Build sources from config (`GILES_CONFIG` → `backend/config.json` → `backend/config.example.json`), with API keys from environment variables
- Fix `config.example.json`, which was invalid JSON because of a comment; add `type` and `apiKeyEnv` to the schema
- Search all enabled sources by default; tag results with `source`
- Fall back to each source's backup scraper when its API fails
- Add an `arxiv` source type using the official Atom API; keep the HTML scraper as backup; 15-second timeouts
- Apply search filters to results (previously accepted and ignored)
- Add CORS for the React dev server and extension origins
- Frontend: call `/search`; treat an unchecked Open Access box as no filter
- Extension: render results with `textContent` instead of `innerHTML`; host permission for the local backend
- **BREAKING**: `/external_api` no longer accepts the hardcoded `external-demo-key`; it uses `EXTERNAL_API_KEY` and is disabled when unset
- Read `SECRET_KEY` from the environment
- Test runner fails when a module fails to import
- Add `.gitignore`; untrack `node_modules`, `frontend/build`, `__pycache__` and logs

## Impact
- Affected specs: `library-search` (new)
- Affected code: `backend/app.py`, `api_client.py`, `mcp_resource.py`, `source_manager.py`, `search_filters.py`, `arxiv_resource.py` (new), `arxiv_scraper.py`, `web_scraper.py`, `uc_library_scraper.py`, `config.example.json`, `config.schema.json`, `test_master.py`, `test_sources.py` (new), `frontend/src/api.js`, `extension/popup.js`, `extension/manifest.json`, `start_all.ps1`
- UC Library ships disabled (`enabled: false`) until a real endpoint and key exist
