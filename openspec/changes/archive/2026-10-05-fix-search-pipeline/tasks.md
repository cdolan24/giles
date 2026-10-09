## 1. Sources and config
- [x] 1.1 Make `config.example.json` valid JSON; add `type` and `apiKeyEnv`; disable UC by default
- [x] 1.2 `SourceManager.build_resources()` builds resources and backup scrapers from config, with keys from env
- [x] 1.3 `app.py` loads resources from `SourceManager` instead of the hardcoded test URL
- [x] 1.4 `ArxivResource` on the official Atom API; normalize the HTML scraper's output to the same fields
- [x] 1.5 Request timeouts; scrapers tolerate missing elements

## 2. Search
- [x] 2.1 Search all enabled sources when `library` is omitted
- [x] 2.2 Fall back to the backup scraper when a source's API fails
- [x] 2.3 Apply filters to results (`filter_results`)
- [x] 2.4 CORS middleware (`CORS_ORIGINS`, extension origins)

## 3. Clients
- [x] 3.1 Frontend calls `/search`; base URL from `REACT_APP_API_URL`; skip unchecked boolean filters
- [x] 3.2 Extension: safe rendering, result links, host permission for the local backend

## 4. Security and hygiene
- [x] 4.1 `SECRET_KEY` and `EXTERNAL_API_KEY` from the environment
- [x] 4.2 `.gitignore`; untrack generated files
- [x] 4.3 `start_all.ps1` installs dependencies into `.venv`

## 5. Tests and docs
- [x] 5.1 Fix test imports; runner fails on import errors
- [x] 5.2 Add `test_sources.py` (fallback, arXiv parsing, config, filters, endpoint, CORS)
- [x] 5.3 README: correct status claims, document config and environment variables
