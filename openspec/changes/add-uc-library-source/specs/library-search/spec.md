## ADDED Requirements

### Requirement: Primo source
The `primo` source type SHALL query the Ex Libris Primo search API with the configured view and scope, authenticate with the key from `apiKeyEnv`, and normalize each document to `id`, `title`, `author`, `year`, `journal`, `url` and `open_access`. Filters that Primo supports natively SHALL be sent in the Primo query rather than applied only after fetching.

#### Scenario: UC search
- **WHEN** the UC Library source is enabled with a valid key and a client calls `/search?q=qubits&library=UC%20Library`
- **THEN** results come from UC Library Search, each with `source: "UC Library"` and the shared result fields

#### Scenario: Primo unavailable
- **WHEN** the Primo API returns an error
- **THEN** the UC backup scraper's results are returned if it is configured, otherwise UC contributes no results
