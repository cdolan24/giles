
from fastapi import FastAPI, Query
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import jwt
import datetime
from typing import List, Dict, Any, Optional
from api_client import LibraryAPIClient, MCPResource
from search_filters import apply_filters
import uvicorn

app = FastAPI()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

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
            raise HTTPException(status_code=404, detail="User not found")
        # Dummy analytics for demo
        analytics = {
            "engagement": 42,
            "popular_topics": ["Quantum Computing", "AI"],
            "system_performance": "Good"
        }
        return {"analytics": analytics}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
@app.get("/external_api")
def external_api_access(api_key: str):
    """
    Provide API for third-party integrations (search, recommendations).
    """
    # For demo, just check API key
    if api_key != "external-demo-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
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
            raise HTTPException(status_code=404, detail="User or peer not found")
        # Dummy logic: append item to peer's bookmarks
        if hasattr(peer, "bookmarks"):
            peer.bookmarks.append(item)
        return {"msg": f"Item shared with {peer_username}"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
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
            raise HTTPException(status_code=404, detail="User not found")
        # Dummy notifications for demo
        notifications = [
            {"type": "publication", "msg": "New paper in Quantum Computing"},
            {"type": "update", "msg": "Your bookmarked paper has new citations"}
        ]
        return {"notifications": notifications}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
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
            raise HTTPException(status_code=404, detail="User not found")
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
            raise HTTPException(status_code=400, detail="Unsupported format")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
@app.get("/recommendations")
def get_personalized_recommendations(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Dummy logic: recommend based on bookmarks and saved searches
        recommendations = []
        if user.bookmarks:
            recommendations.extend(user.bookmarks)
        if user.saved_searches:
            recommendations.extend(user.saved_searches)
        # In production, use ML or collaborative filtering here
        return {"recommendations": recommendations}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
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
from api_client import LibraryAPIClient, MCPResource
from search_filters import apply_filters
import uvicorn

app = FastAPI()

# Example: Load resources from config (hardcoded for now)
resources = [
    MCPResource(name="UC Library", base_url="https://uclibrary.example.edu/api", api_key="<your-api-key>")
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
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    users_db[username] = user
    return {"msg": "User registered successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
    filters = {
        "author": author,
        "year": year,
        "journal": journal,
        "open_access": open_access,
        "citation_count": citation_count
    }
    params = apply_filters({"q": q}, filters)
    try:
        results = client.search_papers(params["q"], library)
        if not results:
            return {"error": "No results found or all sources failed.", "error_code": "NO_RESULTS"}
        return results
    except Exception as e:
        import traceback
        print(f"ERROR_CODE:SEARCH_FAIL | {type(e).__name__}: {e}")
        traceback.print_exc()
        return {"error": str(e), "error_code": "SEARCH_FAIL"}

@app.get("/metadata/{paper_id}")
def get_metadata(paper_id: str, library: str) -> Dict[str, Any]:
    return client.get_metadata(paper_id, library)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
