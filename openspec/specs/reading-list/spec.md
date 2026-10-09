# reading-list Specification

## Purpose
Let users keep papers and searches they care about, share papers with each other, be notified of shares, and export citations.

## Requirements

### Requirement: Bookmarks
Logged-in users SHALL be able to list (`GET /bookmarks`, newest first), add (`POST /bookmarks`) and delete (`DELETE /bookmarks/{id}`) bookmarks. `POST /bookmarks` SHALL accept a `/search` result as-is, reading the paper ID from `paper_id` or `id` and ignoring unknown fields. Adding a paper whose `url` is already bookmarked SHALL return the existing bookmark with 200 instead of 201.

#### Scenario: Bookmark a search result
- **WHEN** a user posts an object returned by `/search`
- **THEN** a bookmark is created with its `paper_id`, `title`, `author`, `year`, `journal`, `url` and `source`

#### Scenario: Another user's bookmark
- **WHEN** a user deletes a bookmark ID that belongs to someone else
- **THEN** the response is 404 with `error_code: "BOOKMARK_NOT_FOUND"`

### Requirement: Saved searches
Logged-in users SHALL be able to list, add (`{query, filters}`) and delete saved searches at `/saved_searches`. Deleting another user's saved search SHALL respond 404 with `SAVED_SEARCH_NOT_FOUND`.

#### Scenario: Save with filters
- **WHEN** a user saves `{"query": "qubits", "filters": {"year": 2024}}`
- **THEN** listing saved searches returns it with the same filters

### Requirement: Sharing
`POST /share` with `{peer_username, item}` SHALL add `item` to the peer's bookmarks with `shared_by` set to the sender and create a `share` notification for the peer. Sharing with a user who doesn't exist SHALL respond 404 with `USER_OR_PEER_NOT_FOUND`; sharing with yourself SHALL respond 400 with `CANNOT_SHARE_WITH_SELF`.

#### Scenario: Share a paper
- **WHEN** alice shares a paper with bob
- **THEN** bob's bookmarks include it with `shared_by: "alice"` and bob has an unread notification about it

### Requirement: Notifications
`GET /notifications` SHALL return the user's 50 most recent notifications, newest first, optionally only unread ones (`unread_only=true`). `POST /notifications/{id}/read` SHALL mark one as read and respond 204.

#### Scenario: Mark read
- **WHEN** a user marks their only notification read
- **THEN** `/notifications?unread_only=true` returns an empty list

### Requirement: Citation export
`POST /export_citations?format=` SHALL export the user's bookmarks as `bibtex` (BibTeX text), `zotero` or `endnote` (JSON, placeholder formats). Any other format SHALL respond 400 with `UNSUPPORTED_FORMAT`.

#### Scenario: BibTeX
- **WHEN** a user with one bookmark exports `bibtex`
- **THEN** the response contains an `@article` entry with the bookmark's title
