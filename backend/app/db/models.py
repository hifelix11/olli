"""Tables. Attempts are raw events and are never updated or deleted."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_id() -> str:
    return str(uuid4())


def now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Child(Base):
    __tablename__ = "children"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Mastery(Base):
    """Learner state per child and competency. Rows exist only for practised competencies."""

    __tablename__ = "mastery"

    child_id: Mapped[str] = mapped_column(ForeignKey("children.id"), primary_key=True)
    competency: Mapped[str] = mapped_column(String(64), primary_key=True)
    p_known: Mapped[float]
    wrong_streak: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class TaskRow(Base):
    """A task handed to a child. The payload holds the full task including the answer."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id"))
    competency: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), unique=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id"))
    competency: Mapped[str] = mapped_column(String(64))
    answer: Mapped[Any] = mapped_column(JSON)
    correct: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
