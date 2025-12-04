"""
FastAPI backend server for UC Library Web-Scraper Extension
"""

from fastapi import FastAPI, Query
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import jwt
import datetime
from typing import List, Dict, Any, Optional
from backend.api_client import LibraryAPIClient, MCPResource
from backend.search_filters import apply_filters
import uvicorn
import logging
import os

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure file logging
file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

# Add console logging for debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Add a debug statement to print critical information directly to the console
print("Debug: Backend server started. Awaiting requests...")

# Example: Load resources from config (hardcoded for now)
resources = [
    MCPResource(name="UC Library", base_url="https://jsonplaceholder.typicode.com", api_key="<your-api-key>")
]
client = LibraryAPIClient(resources)

# User authentication setup
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    saved_searches: Optional[list] = []
    bookmarks: Optional[list] = []
    progress: Optional[dict] = {}

# In-memory user store for demo (replace with DB in production)
users_db = {}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(username: str, email: str, password: str):
    if username in users_db:
        raise HTTPException(status_code=400, detail={"error": "Username already registered", "error_code": "USERNAME_EXISTS"})
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    users_db[username] = user
    return {"msg": "User registered successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "Incorrect username or password", "error_code": "AUTH_FAIL"})
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "User not found", "error_code": "USER_NOT_FOUND"})
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})

@app.get("/analytics")
def get_usage_analytics(token: str = Depends(oauth2_scheme)):
    """
    Return usage analytics dashboard data (user engagement, popular topics, system performance).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "User not found", "error_code": "USER_NOT_FOUND"})
        # Dummy analytics for demo
        analytics = {
            "engagement": 42,
            "popular_topics": ["Quantum Computing", "AI"],
            "system_performance": "Good"
        }
        return {"analytics": analytics}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})
@app.get("/external_api")
def external_api_access(api_key: str):
    """
    Provide API for third-party integrations (search, recommendations).
    """
    # For demo, just check API key
    if api_key != "external-demo-key":
        raise HTTPException(status_code=401, detail={"error": "Invalid API key", "error_code": "API_KEY_INVALID"})
    # Return dummy data
    return {"msg": "Third-party API access granted", "data": ["search", "recommendations"]}
@app.post("/share")
def share_with_peer(peer_username: str, item: dict, token: str = Depends(oauth2_scheme)):
    """
    Share search results, reading lists, or notes with another user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        peer = users_db.get(peer_username)
        if not user or not peer:
            raise HTTPException(status_code=404, detail={"error": "User or peer not found", "error_code": "USER_OR_PEER_NOT_FOUND"})
        # Dummy logic: append item to peer's bookmarks
        if hasattr(peer, "bookmarks"):
            peer.bookmarks.append(item)
        return {"msg": f"Item shared with {peer_username}"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})
@app.get("/notifications")
def get_notifications(token: str = Depends(oauth2_scheme)):
    """
    Return notifications and alerts for the user (new publications, updates).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "User not found", "error_code": "USER_NOT_FOUND"})
        # Dummy notifications for demo
        notifications = [
            {"type": "publication", "msg": "New paper in Quantum Computing"},
            {"type": "update", "msg": "Your bookmarked paper has new citations"}
        ]
        return {"notifications": notifications}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})
@app.post("/export_citations")
def export_citations(format: str, token: str = Depends(oauth2_scheme)):
    """
    Export user citations to supported formats: zotero, endnote, bibtex
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "User not found", "error_code": "USER_NOT_FOUND"})
        # Dummy citations for demo
        citations = getattr(user, "bookmarks", [])
        if format == "bibtex":
            bibtex_entries = []
            for c in citations:
                bibtex_entries.append(f"@article{{{c.get('author','unknown')}{c.get('year','')}, author={{ {c.get('author','')} }}, title={{ {c.get('title','')} }}, journal={{ {c.get('journal','')} }}, year={{ {c.get('year','')} }} }}")
            return {"bibtex": "\n".join(bibtex_entries)}
        elif format == "zotero":
            # Placeholder: return as JSON
            return {"zotero": citations}
        elif format == "endnote":
            # Placeholder: return as JSON
            return {"endnote": citations}
        else:
            raise HTTPException(status_code=400, detail={"error": "Unsupported format", "error_code": "UNSUPPORTED_FORMAT"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})
@app.get("/recommendations")
def get_personalized_recommendations(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "User not found", "error_code": "USER_NOT_FOUND"})
        # Dummy logic: recommend based on bookmarks and saved searches
        recommendations = []
        if user.bookmarks:
            recommendations.extend(user.bookmarks)
        if user.saved_searches:
            recommendations.extend(user.saved_searches)
        # In production, use ML or collaborative filtering here
        return {"recommendations": recommendations}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail={"error": "Invalid token", "error_code": "TOKEN_INVALID"})
@app.get("/search")
def search_papers(
    q: str = Query(..., description="Query string"),
    library: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    journal: Optional[str] = None,
    open_access: Optional[bool] = None,
    citation_count: Optional[int] = None
) -> List[Dict[str, Any]]:
    logging.debug(f"Received search request with query: {q}, library: {library}")
    filters = {
        "author": author,
        "year": year,
        "journal": journal,
        "open_access": open_access,
        "citation_count": citation_count
    }
    params = apply_filters({"q": q}, filters)
    # Fixing type mismatch for `library` parameter
    if library is None:
        library = "default_library"  # Replace with a valid default value

    # Fixing return type issues
    try:
        results = client.search_papers(params["q"], library)
        logging.info(f"Search results: {results}")
        if not results:
            logging.warning("No results found or all sources failed.")
            return [{"error": "No results found or all sources failed.", "error_code": "NO_RESULTS"}]
        # Ensure all error responses in results have error_code
        for r in results:
            if isinstance(r, dict) and "error" in r and "error_code" not in r:
                r["error_code"] = "SEARCH_FAIL"
        return results
    except Exception as e:
        logging.error(f"Error in /search endpoint: {e}", exc_info=True)
        return [{"error": str(e), "error_code": "SEARCH_FAIL"}]

@app.get("/metadata/{paper_id}")
def get_metadata(paper_id: str, library: str) -> Dict[str, Any]:
    return client.get_metadata(paper_id, library)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
