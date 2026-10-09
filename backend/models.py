"""
Database tables for users, bookmarks, saved searches, notifications and search analytics.
"""
import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime.datetime] = mapped_column(default=utcnow)

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="user", foreign_keys="Bookmark.user_id", cascade="all, delete-orphan")
    saved_searches: Mapped[list["SavedSearch"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    paper_id: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(Text)
    year: Mapped[Optional[int]]
    journal: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(128))
    shared_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime.datetime] = mapped_column(default=utcnow)

    user: Mapped[User] = relationship(back_populates="bookmarks", foreign_keys=[user_id])
    shared_by: Mapped[Optional[User]] = relationship(foreign_keys=[shared_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "journal": self.journal,
            "url": self.url,
            "source": self.source,
            "shared_by": self.shared_by.username if self.shared_by else None,
            "created_at": self.created_at.isoformat(),
        }


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    query: Mapped[str] = mapped_column(Text)
    filters: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime.datetime] = mapped_column(default=utcnow)

    user: Mapped[User] = relationship(back_populates="saved_searches")

    def to_dict(self):
        return {"id": self.id, "query": self.query, "filters": self.filters, "created_at": self.created_at.isoformat()}


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(32))
    msg: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=utcnow)

    user: Mapped[User] = relationship(back_populates="notifications")

    def to_dict(self):
        return {"id": self.id, "type": self.type, "msg": self.msg, "read": self.read, "created_at": self.created_at.isoformat()}


class SearchLog(Base):
    """One row per /search request; feeds the analytics endpoint."""
    __tablename__ = "search_log"
    __table_args__ = (Index("ix_search_log_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    query: Mapped[str] = mapped_column(Text)
    result_count: Mapped[int]
    duration_ms: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(default=utcnow)
