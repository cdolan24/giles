"""
FastAPI backend server for UC Library Web-Scraper Extension
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Response
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, AliasChoices
from sqlalchemy import select, func, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import bcrypt
import jwt
import datetime
import time
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from backend.api_client import LibraryAPIClient
from backend.source_manager import SourceManager
from backend.search_filters import filter_results
from backend.database import get_db, init_db
from backend.models import User, Bookmark, SavedSearch, Notification, SearchLog, utcnow
import uvicorn
import logging
import os
import secrets


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Configure logging (console + logs/app.log at the project root)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG", "").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler()
    ]
)

# Browser clients (React dev server, extension popup) call this API cross-origin
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load library resources from config (see backend/source_manager.py)
resources = SourceManager().build_resources()
logging.info(f"Loaded library sources: {[r.name for r in resources]}")
client = LibraryAPIClient(resources)

# User authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)
    logging.warning("SECRET_KEY not set; using a random key. Login tokens will not survive a restart.")
EXTERNAL_API_KEY = os.environ.get("EXTERNAL_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
BCRYPT_MAX_BYTES = 72
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def error(status_code: int, message: str, code: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error": message, "error_code": code})


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        return False


def find_user(db: Session, username: str) -> Optional[User]:
    return db.scalar(select(User).where(User.username == username))


def authenticate_user(db: Session, username: str, password: str):
    user = find_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise error(401, "Invalid token", "TOKEN_INVALID")
    user = find_user(db, payload.get("sub", ""))
    if not user:
        raise error(404, "User not found", "USER_NOT_FOUND")
    return user


def get_optional_user(token: Optional[str] = Depends(optional_oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    return find_user(db, payload.get("sub", ""))


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    email: str = Field(max_length=255, pattern=r"^[^@\s]+@[^@\s]+$")
    password: str = Field(min_length=8)


class PaperIn(BaseModel):
    """A paper as returned by /search; extra fields (abstract, etc.) are ignored."""
    title: str = Field(min_length=1)
    paper_id: Optional[str] = Field(default=None, validation_alias=AliasChoices("paper_id", "id"))
    author: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None


class SavedSearchIn(BaseModel):
    query: str = Field(min_length=1)
    filters: Dict[str, Any] = {}


class ShareRequest(BaseModel):
    peer_username: str
    item: PaperIn


def add_bookmark(db: Session, user: User, paper: PaperIn, shared_by: Optional[User] = None):
    """Create a bookmark, or return the existing one for the same URL. Returns (bookmark, created)."""
    if paper.url:
        existing = db.scalar(select(Bookmark).where(Bookmark.user_id == user.id, Bookmark.url == paper.url))
        if existing:
            return existing, False
    bookmark = Bookmark(user_id=user.id, shared_by_id=shared_by.id if shared_by else None, **paper.model_dump())
    db.add(bookmark)
    return bookmark, True


@app.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if len(body.password.encode()) > BCRYPT_MAX_BYTES:
        raise error(400, f"Password must be at most {BCRYPT_MAX_BYTES} bytes", "PASSWORD_TOO_LONG")
    if find_user(db, body.username):
        raise error(400, "Username already registered", "USERNAME_EXISTS")
    db.add(User(username=body.username, email=body.email, hashed_password=get_password_hash(body.password)))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise error(400, "Username already registered", "USERNAME_EXISTS")
    return {"msg": "User registered successfully"}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "Incorrect username or password", "error_code": "AUTH_FAIL"})
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/profile")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    unread = db.scalar(select(func.count()).select_from(Notification).where(Notification.user_id == user.id, Notification.read.is_(False)))
    return {
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "bookmarks": len(user.bookmarks),
        "saved_searches": len(user.saved_searches),
        "unread_notifications": unread,
    }


@app.get("/bookmarks")
def list_bookmarks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Bookmark).where(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc(), Bookmark.id.desc()))
    return {"bookmarks": [b.to_dict() for b in rows]}


@app.post("/bookmarks", status_code=201)
def create_bookmark(paper: PaperIn, response: Response, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark, created = add_bookmark(db, user, paper)
    db.commit()
    if not created:
        response.status_code = 200
    return bookmark.to_dict()


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark = db.get(Bookmark, bookmark_id)
    if not bookmark or bookmark.user_id != user.id:
        raise error(404, "Bookmark not found", "BOOKMARK_NOT_FOUND")
    db.delete(bookmark)
    db.commit()


@app.get("/saved_searches")
def list_saved_searches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(SavedSearch).where(SavedSearch.user_id == user.id).order_by(SavedSearch.created_at.desc(), SavedSearch.id.desc()))
    return {"saved_searches": [s.to_dict() for s in rows]}


@app.post("/saved_searches", status_code=201)
def create_saved_search(body: SavedSearchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = SavedSearch(user_id=user.id, query=body.query, filters=body.filters)
    db.add(saved)
    db.commit()
    return saved.to_dict()


@app.delete("/saved_searches/{search_id}", status_code=204)
def delete_saved_search(search_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.get(SavedSearch, search_id)
    if not saved or saved.user_id != user.id:
        raise error(404, "Saved search not found", "SAVED_SEARCH_NOT_FOUND")
    db.delete(saved)
    db.commit()


@app.get("/analytics")
def get_usage_analytics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Return usage analytics dashboard data (user engagement, popular topics, system performance).
    """
    now = utcnow()
    month_ago = now - datetime.timedelta(days=30)
    day_ago = now - datetime.timedelta(days=1)

    topic = func.lower(SearchLog.query)
    popular = db.execute(
        select(topic, func.count().label("n"))
        .where(SearchLog.created_at >= month_ago)
        .group_by(topic).order_by(func.count().desc()).limit(5)
    ).all()

    searches_24h, avg_ms, empty_24h = db.execute(
        select(func.count(), func.avg(SearchLog.duration_ms), func.sum(case((SearchLog.result_count == 0, 1), else_=0)))
        .where(SearchLog.created_at >= day_ago)
    ).one()

    analytics = {
        "engagement": {
            "searches": db.scalar(select(func.count()).select_from(SearchLog).where(SearchLog.user_id == user.id)),
            "bookmarks": len(user.bookmarks),
            "saved_searches": len(user.saved_searches),
        },
        "popular_topics": [{"query": q, "count": n} for q, n in popular],
        "system_performance": {
            "searches_last_24h": searches_24h,
            "avg_search_ms": round(avg_ms) if avg_ms is not None else None,
            "no_result_rate": round((empty_24h or 0) / searches_24h, 3) if searches_24h else None,
        },
    }
    return {"analytics": analytics}


@app.get("/external_api")
def external_api_access(api_key: str):
    """
    Provide API for third-party integrations (search, recommendations).
    """
    if not EXTERNAL_API_KEY:
        raise HTTPException(status_code=503, detail={"error": "External API access is not configured", "error_code": "API_KEY_NOT_CONFIGURED"})
    if not secrets.compare_digest(api_key, EXTERNAL_API_KEY):
        raise HTTPException(status_code=401, detail={"error": "Invalid API key", "error_code": "API_KEY_INVALID"})
    # Return dummy data
    return {"msg": "Third-party API access granted", "data": ["search", "recommendations"]}


@app.post("/share")
def share_with_peer(body: ShareRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Share a paper with another user: it is added to their bookmarks and they get a notification.
    """
    peer = find_user(db, body.peer_username)
    if not peer:
        raise error(404, "User or peer not found", "USER_OR_PEER_NOT_FOUND")
    if peer.id == user.id:
        raise error(400, "Cannot share with yourself", "CANNOT_SHARE_WITH_SELF")
    add_bookmark(db, peer, body.item, shared_by=user)
    db.add(Notification(user_id=peer.id, type="share", msg=f'{user.username} shared "{body.item.title}" with you'))
    db.commit()
    return {"msg": f"Item shared with {peer.username}"}


@app.get("/notifications")
def get_notifications(unread_only: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Return the user's most recent notifications (newest first).
    """
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.read.is_(False))
    rows = db.scalars(stmt.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(50))
    return {"notifications": [n.to_dict() for n in rows]}


@app.post("/notifications/{notification_id}/read", status_code=204)
def mark_notification_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise error(404, "Notification not found", "NOTIFICATION_NOT_FOUND")
    notification.read = True
    db.commit()


@app.post("/export_citations")
def export_citations(format: str, user: User = Depends(get_current_user)):
    """
    Export the user's bookmarks to supported formats: zotero, endnote, bibtex
    """
    citations = [b.to_dict() for b in user.bookmarks]
    if format == "bibtex":
        bibtex_entries = []
        for c in citations:
            bibtex_entries.append(f"@article{{{c.get('author') or 'unknown'}{c.get('year') or ''}, author={{ {c.get('author') or ''} }}, title={{ {c.get('title') or ''} }}, journal={{ {c.get('journal') or ''} }}, year={{ {c.get('year') or ''} }} }}")
        return {"bibtex": "\n".join(bibtex_entries)}
    elif format == "zotero":
        # Placeholder: return as JSON
        return {"zotero": citations}
    elif format == "endnote":
        # Placeholder: return as JSON
        return {"endnote": citations}
    else:
        raise HTTPException(status_code=400, detail={"error": "Unsupported format", "error_code": "UNSUPPORTED_FORMAT"})


@app.get("/recommendations")
def get_personalized_recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Re-run the user's most recent saved searches and searches, excluding papers they've already bookmarked.
    """
    queries: List[tuple] = []
    for s in sorted(user.saved_searches, key=lambda s: s.created_at, reverse=True):
        queries.append((s.query, s.filters or {}))
    recent = db.scalars(select(SearchLog.query).where(SearchLog.user_id == user.id).order_by(SearchLog.created_at.desc()).limit(20))
    queries.extend((q, {}) for q in recent)

    seen_queries, picked = set(), []
    for q, filters in queries:
        if q.lower() not in seen_queries:
            seen_queries.add(q.lower())
            picked.append((q, filters))
        if len(picked) == 3:
            break

    seen = {b.url or b.title.lower() for b in user.bookmarks}
    recommendations = []
    for q, filters in picked:
        for paper in filter_results(client.search_papers(q), filters):
            key = paper.get("url") or str(paper.get("title", "")).lower()
            if key and key not in seen:
                seen.add(key)
                recommendations.append(paper)
    return {"recommendations": recommendations[:10], "based_on": [q for q, _ in picked]}


@app.get("/search")
def search_papers(
    q: str = Query(..., description="Query string"),
    library: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    journal: Optional[str] = None,
    open_access: Optional[bool] = None,
    citation_count: Optional[int] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    logging.debug(f"Received search request with query: {q}, library: {library}")
    filters = {
        "author": author,
        "year": year,
        "journal": journal,
        "open_access": open_access,
        "citation_count": citation_count
    }
    started = time.perf_counter()
    try:
        results = client.search_papers(q, library)
        results = filter_results(results, filters)
    except Exception as e:
        logging.error(f"Error in /search endpoint: {e}", exc_info=True)
        return [{"error": str(e), "error_code": "SEARCH_FAIL"}]
    log_search(db, user, q, len(results), started)
    logging.info(f"Search for {q!r} returned {len(results)} results")
    if not results:
        logging.warning("No results found or all sources failed.")
        return [{"error": "No results found or all sources failed.", "error_code": "NO_RESULTS"}]
    return results


def log_search(db: Session, user: Optional[User], query: str, result_count: int, started: float):
    # Analytics logging must never break search
    try:
        db.add(SearchLog(user_id=user.id if user else None, query=query, result_count=result_count,
                         duration_ms=int((time.perf_counter() - started) * 1000)))
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to log search: {e}")


@app.get("/metadata/{paper_id}")
def get_metadata(paper_id: str, library: str) -> Dict[str, Any]:
    return client.get_metadata(paper_id, library)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
