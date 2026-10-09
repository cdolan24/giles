## ADDED Requirements

### Requirement: Config-driven library sources
The system SHALL build its library sources at startup from the first config file found among: the path in `GILES_CONFIG`, `backend/config.json`, then `backend/config.example.json`. Each library entry SHALL specify `name`, `baseUrl` and `enabled`, and MAY specify `type` (`rest` or `arxiv`, default `rest`), `apiKeyEnv`, `apiKey` and `backupScraper`. Disabled entries SHALL NOT be queried.

#### Scenario: Local config overrides example
- **WHEN** `backend/config.json` exists and `GILES_CONFIG` is unset
- **THEN** sources are loaded from `backend/config.json`

#### Scenario: Disabled source skipped
- **WHEN** a library entry has `enabled: false`
- **THEN** no resource is built for it and searches never query it

### Requirement: API keys from the environment
The system SHALL read a source's API key from the environment variable named by its `apiKeyEnv`, falling back to an inline `apiKey`, and SHALL send it as `Authorization: Bearer <key>` on requests to that source. The system SHALL NOT print or log key values.

#### Scenario: Key supplied by environment
- **WHEN** a source has `apiKeyEnv: "API_KEY_UC_LIBRARY"` and that variable is set
- **THEN** requests to the source carry `Authorization: Bearer <value>`

### Requirement: Search across sources
`GET /search?q=` SHALL query every enabled source when `library` is omitted, or only the named source when `library` is given, and SHALL tag each result with the `source` it came from. Source requests SHALL time out after 15 seconds.

#### Scenario: Default searches all sources
- **WHEN** a client calls `/search?q=qubits` without `library`
- **THEN** results from all enabled sources are returned, each with a `source` field

### Requirement: Backup scraper fallback
When a source's API request fails or returns an error, the system SHALL run that source's backup scraper, if configured, and return its results instead. A failing scraper SHALL contribute no results without failing the whole search.

#### Scenario: API down, scraper succeeds
- **WHEN** the arXiv API returns an error and the arXiv HTML scraper succeeds
- **THEN** `/search` returns the scraper's results tagged `source: "arXiv"`

### Requirement: arXiv source
The `arxiv` source type SHALL query the official arXiv Atom API and normalize each entry to `id`, `title`, `author` (comma-separated), `year`, `journal` (journal reference or `"arXiv"`), `abstract`, `url` and `open_access: true`. `metadata/{id}` SHALL look up a single paper by arXiv ID.

#### Scenario: Metadata lookup
- **WHEN** a client calls `/metadata/2211.02350?library=arXiv`
- **THEN** the paper's normalized metadata is returned

### Requirement: Result filters
`/search` SHALL accept `author` and `journal` (case-insensitive substring), `year` (exact), `open_access` (exact) and `citation_count` (minimum) and SHALL drop results that don't match. A result missing a filtered field SHALL be excluded. Omitted filters SHALL NOT restrict results.

#### Scenario: Year filter
- **WHEN** a client calls `/search?q=qubits&year=2024`
- **THEN** only results with `year` 2024 are returned

#### Scenario: Citation filter on a source without citation data
- **WHEN** `citation_count` is set and results come only from arXiv
- **THEN** no results are returned, because arXiv results have no citation count

### Requirement: Search error contract
`/search` SHALL respond with HTTP 200 and a list. When no results remain, the list SHALL contain one object with `error` and `error_code: "NO_RESULTS"`. When an unexpected error occurs, the object SHALL have `error_code: "SEARCH_FAIL"`.

#### Scenario: Nothing found
- **WHEN** every source fails or returns nothing
- **THEN** the response is `[{"error": "No results found or all sources failed.", "error_code": "NO_RESULTS"}]`

### Requirement: Browser client access
The backend SHALL allow cross-origin requests from the origins listed in `CORS_ORIGINS` (default `http://localhost:3000` and `http://127.0.0.1:3000`) and from any `chrome-extension://` origin.

#### Scenario: React dev server
- **WHEN** the frontend at `http://localhost:3000` calls `/search`
- **THEN** the response includes `Access-Control-Allow-Origin: http://localhost:3000`

### Requirement: Third-party API key
`GET /external_api` SHALL compare its `api_key` against `EXTERNAL_API_KEY` in constant time. When `EXTERNAL_API_KEY` is unset, the endpoint SHALL respond 503 with `API_KEY_NOT_CONFIGURED`.

#### Scenario: Not configured
- **WHEN** `EXTERNAL_API_KEY` is unset and any key is sent
- **THEN** the response is 503 with `error_code: "API_KEY_NOT_CONFIGURED"`
