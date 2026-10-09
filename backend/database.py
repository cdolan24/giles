"""
Database engine and session setup.

Uses DB_URL if set (any SQLAlchemy URL, e.g. postgresql+psycopg://...),
otherwise a SQLite file at data/giles.db in the project root.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "data", "giles.db")


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            # One shared connection so every session sees the same in-memory DB
            kwargs["poolclass"] = StaticPool
        return create_engine(url, **kwargs)
    return create_engine(url, pool_pre_ping=True)


DB_URL = os.environ.get("DB_URL") or f"sqlite:///{DEFAULT_DB_PATH}"
engine = make_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db(bind=None):
    from backend import models  # noqa: F401  (registers tables on Base.metadata)
    bind = bind or engine
    if bind.url.drivername.startswith("sqlite") and bind.url.database not in (None, "", ":memory:"):
        os.makedirs(os.path.dirname(os.path.abspath(bind.url.database)), exist_ok=True)
    Base.metadata.create_all(bind)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
