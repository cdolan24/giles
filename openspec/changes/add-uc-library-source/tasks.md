## 0. Prerequisites (external)
- [x] 0.1 Request UC Library Search / Primo API access
- [ ] 0.2 Receive API key, regional base URL, and `vid`/`tab`/`scope` values

## 1. Implementation
- [ ] 1.1 Confirm the Primo auth style (query `apikey` vs header) and response shape with a manual request
- [ ] 1.2 `PrimoResource` with search and metadata, normalized to shared result fields
- [ ] 1.3 Register the `primo` type in `SourceManager` and `config.schema.json`
- [ ] 1.4 Map supported filters (year, author, open access) to Primo query parameters
- [ ] 1.5 Update UC entry in `config.example.json` (keep `enabled: false` there; enable in local `config.json`)
- [ ] 1.6 Verify or remove the UC backup scraper against the real search pages

## 2. Tests and docs
- [ ] 2.1 Unit tests with a recorded Primo response (no network)
- [ ] 2.2 Live check with the real key: search, metadata, fallback
- [ ] 2.3 README "Enabling UC Library" steps updated
