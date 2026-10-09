## ADDED Requirements

### Requirement: Search logging
Each `/search` request that completes SHALL be recorded with its query, result count, duration in milliseconds and timestamp, attributed to the user when a valid bearer token is sent and anonymous otherwise. A failure to record SHALL NOT affect the search response. `/search` SHALL NOT require authentication.

#### Scenario: Anonymous search
- **WHEN** a client searches without a token
- **THEN** the search is logged with no user

#### Scenario: Invalid token on search
- **WHEN** a client searches with an invalid token
- **THEN** the search succeeds and is logged as anonymous

### Requirement: Analytics
`GET /analytics` SHALL return, for a logged-in user:
- `engagement`: the user's total searches, bookmarks and saved searches
- `popular_topics`: the 5 most frequent queries across all users in the last 30 days, case-insensitive, as `{query, count}`
- `system_performance`: searches in the last 24 hours, their average duration (`avg_search_ms`) and the fraction that returned no results (`no_result_rate`), with `null` averages when there were none

#### Scenario: Popular topics are case-insensitive
- **WHEN** users searched "Qubits" and "qubits" this month
- **THEN** `popular_topics` includes `{"query": "qubits", "count": 2}`

#### Scenario: Old searches excluded
- **WHEN** the only logged search is older than 30 days
- **THEN** `popular_topics` is empty

### Requirement: Recommendations
`GET /recommendations` SHALL take up to 3 distinct queries (case-insensitive), first from the user's saved searches (newest first) then from their logged searches (newest first). It SHALL re-run each query with its saved filters and return up to 10 results, excluding papers the user has bookmarked (matched by URL, or title when there is no URL) and duplicates. The response SHALL include `based_on` listing the queries used.

#### Scenario: Bookmarked papers excluded
- **WHEN** a saved search returns a paper the user already bookmarked and one they haven't
- **THEN** only the unbookmarked paper is recommended and `based_on` lists the saved query

#### Scenario: New user
- **WHEN** a user has no saved or logged searches
- **THEN** the response is `{"recommendations": [], "based_on": []}`
