from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(engine)


def get_session() -> Iterator[Session]:
    """One transaction per request: commit on success, roll back on error."""
    with SessionLocal.begin() as session:
        yield session
