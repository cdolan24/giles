## Context
Session of 2026-10-05. The question was whether the project only needed a UC API key to be complete. An audit showed the key alone wouldn't help, because the code that would use it was still placeholders, and that search was broken for every source.

### Findings (verified before fixing)
- `TestClient` probe: `/api/search` → 404; `/search?q=x` → `[{"error_code": "NO_RESULTS"}]`; CORS preflight → 405 with no `Access-Control-Allow-Origin`.
- `app.py` built a single `MCPResource` pointing at `https://jsonplaceholder.typicode.com` with `api_key="<your-api-key>"` and never read config.
- `config.example.json` had a `//` comment, so `json.load` in `SourceManager` raised.
- `LibraryAPIClient` never referenced backup scrapers, although the README said it did.
- `MCPResource.query` returned `{"error": ...}` on failure, which the client read as zero results.
- `beautifulsoup4` was in `requirements.txt` but missing from `.venv`; `start_all.ps1` installed into the global Python and then ran the venv's Python.
- `test_master.py` swallowed `ImportError` for `test_api_client` and `test_backend` (they mixed bare and `backend.*` imports) and still exited 0.
- About 41,800 `frontend/node_modules` files were tracked in git.
- The December session log said endpoints were served under `/api/search`; the code never had that prefix.
- The README claimed the backend accepted a `lang` parameter; no such code existed.

## Goals / Non-Goals
- Goals: make search work end to end with at least one real source; make the UC source configurable without code changes; make the test suite trustworthy.
- Non-Goals: the real UC integration (blocked on Primo access), multi-language support, ranking.

## Decisions
- **arXiv via the official API, with the HTML scraper as backup.** arXiv asks clients to use the API, and it needs no key. This gives the fallback path a real exercise: API first, scraper second.
- **Resource types instead of per-source branches.** `type: "rest" | "arxiv"` maps to an `MCPResource` subclass. Primo will need its own type because its responses aren't `{"results": [...]}`.
- **Keys by env var name (`apiKeyEnv`).** Committed config never holds secrets; inline `apiKey` remains for an untracked `config.json`.
- **Filter after fetching.** Neither the generic REST shape nor the arXiv API supports these filters uniformly. Trade-off: filters only see the first page of results (10 from arXiv).
- **UC disabled by default.** With a placeholder URL it would only add failing requests and log noise.
- **Serve `/search`, not `/api/search`.** The extension and `/metadata` already used unprefixed paths; fixing the one frontend call was the smaller change.

## Risks / Trade-offs
- The UC scraper's URL and selectors are guesses inherited from the original code → documented as placeholders, and the source is disabled.
- `citation_count` excludes all arXiv results (no citation data) → noted in spec; fix by adding Semantic Scholar or Crossref.
- Untracking `node_modules` creates a 41k-file deletion commit → isolated in its own commit (`d0f3b86b`).

## Verification
- `python backend/test_master.py`: 21 tests, all modules loaded.
- Live: `/search?q=quantum error correction` returned 10 arXiv results; with `year=2026&open_access=true`, 1; `/metadata/2211.02350?library=arXiv` returned "Tierkreis…"; `/external_api` with the old demo key → 503.
- Live HTML scraper (backup path): 50 results for "quantum computing".
- Not verified in a browser: the React app and the extension popup.

## Follow-ups
- UC Library source → `changes/add-uc-library-source`
- Wire the ranking engine, summarizer, entity linker and prerequisite recommender into endpoints (they pass unit tests but no endpoint calls them)
- Citation counts (Semantic Scholar / Crossref)
- Multi-language support (not started)
- Real Zotero/EndNote export formats
