## ADDED Requirements

### Requirement: Persistent storage
User data SHALL be stored in the database at `DB_URL`, defaulting to a SQLite file at `data/giles.db`. Missing tables SHALL be created on startup. Data SHALL survive server restarts.

#### Scenario: Restart
- **WHEN** a user registers and the server is restarted with the same database
- **THEN** the user can log in with the same credentials

### Requirement: Registration
`POST /register` SHALL accept a JSON body `{username, email, password}` and respond 201 on success. Usernames SHALL be 3–64 characters of letters, digits, `_`, `.` or `-` and unique. Passwords SHALL be at least 8 characters and at most 72 bytes, and SHALL be stored only as bcrypt hashes.

#### Scenario: Duplicate username
- **WHEN** a username that already exists is registered
- **THEN** the response is 400 with `error_code: "USERNAME_EXISTS"`

#### Scenario: Password too long for bcrypt
- **WHEN** the password is longer than 72 bytes
- **THEN** the response is 400 with `error_code: "PASSWORD_TOO_LONG"`

### Requirement: Login tokens
`POST /token` SHALL accept form fields `username` and `password` and return an HS256 JWT bearer token valid for 30 minutes, signed with `SECRET_KEY`. If `SECRET_KEY` is unset, the server SHALL generate a random key at startup and log a warning that tokens won't survive a restart.

#### Scenario: Wrong password
- **WHEN** the password doesn't match
- **THEN** the response is 401 with `error_code: "AUTH_FAIL"`

### Requirement: Authenticated requests
Endpoints that require a user SHALL respond 401 when no bearer token is sent (FastAPI's default `{"detail": "Not authenticated"}`), 401 with `TOKEN_INVALID` for an expired or invalid token, and 404 with `USER_NOT_FOUND` when the token's user no longer exists.

#### Scenario: Expired token
- **WHEN** a request carries a token older than 30 minutes
- **THEN** the response is 401 with `error_code: "TOKEN_INVALID"`

### Requirement: Profile
`GET /profile` SHALL return the user's `username`, `email`, `created_at`, and counts of `bookmarks`, `saved_searches` and `unread_notifications`. It SHALL NOT return the password hash.

#### Scenario: Profile excludes secrets
- **WHEN** a logged-in user calls `/profile`
- **THEN** the response has no `hashed_password` field
