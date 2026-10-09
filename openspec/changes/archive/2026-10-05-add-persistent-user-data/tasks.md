## 1. Persistence
- [x] 1.1 `database.py`: engine from `DB_URL` (SQLite default, `StaticPool` for in-memory), `get_db`, `init_db`
- [x] 1.2 `models.py`: `User`, `Bookmark`, `SavedSearch`, `Notification`, `SearchLog`
- [x] 1.3 Create tables on startup (lifespan)
- [x] 1.4 Ignore `data/`; add `sqlalchemy` and `bcrypt`, remove `passlib`

## 2. Accounts
- [x] 2.1 bcrypt hashing; 72-byte limit
- [x] 2.2 `/register` JSON body with validation
- [x] 2.3 `get_current_user` / `get_optional_user` dependencies
- [x] 2.4 `/profile` without the password hash

## 3. Reading list
- [x] 3.1 Bookmarks CRUD with URL dedupe and `id` alias
- [x] 3.2 Saved searches CRUD
- [x] 3.3 `/share` creates a bookmark and a notification
- [x] 3.4 Notifications list, `unread_only`, mark read
- [x] 3.5 `/export_citations` reads bookmarks

## 4. Insights
- [x] 4.1 Log every `/search`; never fail search on a logging error
- [x] 4.2 `/analytics` from the search log
- [x] 4.3 `/recommendations` from saved and recent searches

## 5. Tests and docs
- [x] 5.1 `test_database.py` (auth, bookmarks, saved searches, sharing, analytics, recommendations, persistence)
- [x] 5.2 Endpoint tests in `test_sources.py` use a test database
- [x] 5.3 README: database, `DB_URL`, user endpoints; session log entry
