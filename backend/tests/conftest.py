import time
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import auth
from app.content import CONTENT_DIR
from app.db.models import Base
from app.db.session import get_session
from app.domain.generators.generate import load_specs
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph
from app.main import app

KEY = ec.generate_private_key(ec.SECP256R1())
PARENT = "11111111-1111-1111-1111-111111111111"


def token_for(sub: str, **claims: Any) -> str:
    """An access token as Supabase Auth signs it."""
    payload = {"sub": sub, "aud": "authenticated", "iss": auth.ISSUER, "exp": time.time() + 3600}
    return jwt.encode(payload | claims, KEY, algorithm="ES256")


def bearer(sub: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_for(sub)}"}


class FakeJwks:
    """Stands in for the public keys that Supabase Auth publishes."""

    def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
        return SimpleNamespace(key=KEY.public_key())


@pytest.fixture(scope="session")
def graph() -> CompetencyGraph:
    return CompetencyGraph.load(CONTENT_DIR / "math" / "competencies.yaml")


@pytest.fixture(scope="session")
def specs(graph: CompetencyGraph) -> dict[str, GeneratorSpec]:
    return load_specs(CONTENT_DIR / "math" / "generators", graph)


@pytest.fixture
def db() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(engine)
    engine.dispose()


@pytest.fixture
def client(db: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Logged in as PARENT, against an in-memory SQLite database."""

    def override() -> Iterator[Session]:
        with db.begin() as session:
            yield session

    monkeypatch.setattr(auth, "jwks", FakeJwks())
    app.dependency_overrides[get_session] = override
    yield TestClient(app, headers=bearer(PARENT))
    app.dependency_overrides.clear()
