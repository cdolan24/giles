## Why
UC Library is the project's primary source, but it is disabled: its URL is a placeholder, and the generic `rest` source type expects `{"results": [...]}`, which Primo doesn't return. API access was requested from UC library systems staff in October 2026 and is pending.

## What Changes
- Add a `primo` source type that queries the Ex Libris Primo search API and normalizes results to the shared fields (`id`, `title`, `author`, `year`, `journal`, `url`, `open_access`)
- Configure the UC Library entry with the real endpoint, view/scope parameters and `apiKeyEnv: "API_KEY_UC_LIBRARY"`; enable it
- Replace the placeholder UC backup scraper URL and selectors with ones verified against the real UC Library Search pages, or remove the scraper if the pages are rendered client-side and can't be scraped
- Pass search filters to Primo where it supports them natively, instead of only filtering the first page afterward

## Impact
- Affected specs: `library-search`
- Affected code: new `backend/primo_resource.py`, `backend/source_manager.py` (register type), `backend/uc_library_scraper.py`, `backend/config.example.json`, `backend/config.schema.json`, tests
- Blocked on: API key, base URL (region, e.g. `api-na.hosted.exlibrisgroup.com`), and the `vid`/`tab`/`scope` values for UC from the campus library

## Open Questions
- Which campus issues the key, and does it cover all UC campuses or one institution's view?
- Rate limits and terms of use for a student-built tool
- Does Primo authenticate with an `apikey` query parameter rather than a bearer header? If so, `MCPResource` needs a configurable auth style.
