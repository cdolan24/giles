## Why
The backend now has persistent accounts, bookmarks, saved searches, sharing, notifications and recommendations, but neither client exposes any of them. Users can only run anonymous searches.

## What Changes
- React app: register and log in; store the token and send it with requests (including `/search`, so searches count toward the user's analytics)
- Bookmark button on each result; bookmarks list with delete
- Save the current query and filters; saved searches list that re-runs a search
- Recommendations panel (showing `based_on`)
- Notifications indicator with unread count from `/profile`; mark as read
- Share a result with another user by username
- Handle token expiry (30 minutes): on `TOKEN_INVALID`, clear the token and prompt to log in again
- Extension: log in and bookmark from the popup (token in `chrome.storage`)

## Impact
- Affected specs: `web-client` (new)
- Affected code: `frontend/src/api.js`, `ChatWidget.js`, new account/bookmark components; `extension/popup.js`
- No backend changes expected
