## ADDED Requirements

### Requirement: Client authentication
The React app SHALL let users register and log in, store the bearer token, and send it with every backend request. When the backend responds with `TOKEN_INVALID`, the app SHALL clear the stored token and ask the user to log in again.

#### Scenario: Logged-in search
- **WHEN** a logged-in user searches
- **THEN** the request carries `Authorization: Bearer <token>`

#### Scenario: Expired session
- **WHEN** a request fails with `TOKEN_INVALID`
- **THEN** the user is logged out and shown the login form

### Requirement: Reading list in the client
The React app SHALL let a logged-in user bookmark a search result, view and delete bookmarks, save and re-run searches, share a result with another user by username, and view recommendations.

#### Scenario: Bookmark from results
- **WHEN** a user clicks bookmark on a search result
- **THEN** the paper appears in their bookmarks view

### Requirement: Notifications in the client
The React app SHALL show the unread notification count and let the user view notifications and mark them read.

#### Scenario: Shared paper
- **WHEN** another user shares a paper with the logged-in user
- **THEN** the unread count increases and the notification is listed
