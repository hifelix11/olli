"""Parent accounts: login through FastAPI, and each parent sees only their own children."""

import time
from typing import Any

import httpx2
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.api import auth
from tests.conftest import PARENT, bearer, token_for

OTHER = "22222222-2222-2222-2222-222222222222"
LOGIN = {"email": "eltern@example.com", "password": "geheim123"}
SESSION = {"access_token": "a", "refresh_token": "r", "token_type": "bearer", "user": {}}


def fake_supabase(
    monkeypatch: pytest.MonkeyPatch, status: int, body: dict[str, Any]
) -> list[httpx2.Request]:
    """Supabase Auth answers every call with this response. Returns the calls."""
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        return httpx2.Response(status, json=body)

    transport = httpx2.MockTransport(handle)
    monkeypatch.setattr(auth, "gotrue", httpx2.Client(base_url=auth.ISSUER, transport=transport))
    return calls


@pytest.mark.parametrize(
    "token",
    [
        "",
        "nonsense",
        token_for(PARENT, exp=time.time() - 10),
        token_for(PARENT, iss="https://example.com/auth/v1"),
        token_for(PARENT, aud="anon"),
        jwt.encode(
            {"sub": PARENT, "aud": "authenticated", "iss": auth.ISSUER, "exp": time.time() + 60},
            ec.generate_private_key(ec.SECP256R1()),
            algorithm="ES256",
        ),
    ],
    ids=["missing", "garbage", "expired", "wrong_issuer", "wrong_audience", "wrong_key"],
)
def test_children_need_a_valid_token(client: TestClient, token: str) -> None:
    res = client.get("/children", headers={"Authorization": f"Bearer {token}" if token else ""})
    assert res.status_code == 401


def test_parent_sees_only_own_children(client: TestClient) -> None:
    other = bearer(OTHER)
    mine = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
    theirs = client.post("/children", json={"name": "Max", "sign": "sun"}, headers=other).json()

    assert client.get("/children").json() == [mine]
    assert client.get("/children", headers=other).json() == [theirs]

    for path in ("next-task", "mastery", "progress"):
        assert client.get(f"/children/{mine['id']}/{path}", headers=other).status_code == 404

    task = client.get(f"/children/{mine['id']}/next-task").json()
    answer = {"task_id": task["id"], "answer": 1}
    for child in (mine, theirs):
        res = client.post(f"/children/{child['id']}/answers", json=answer, headers=other)
        assert res.status_code == 404


def test_login_returns_the_tokens(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = fake_supabase(monkeypatch, 200, SESSION)
    res = client.post("/auth/login", json=LOGIN)
    assert res.json() == {"access_token": "a", "refresh_token": "r"}
    assert calls[0].url.path == "/auth/v1/token"
    assert calls[0].url.params["grant_type"] == "password"


def test_login_passes_the_error_code_on(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_supabase(monkeypatch, 400, {"error_code": "invalid_credentials", "msg": "Invalid"})
    res = client.post("/auth/login", json=LOGIN)
    assert res.status_code == 400
    assert res.json() == {"detail": "invalid_credentials"}


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (SESSION, {"access_token": "a", "refresh_token": "r"}),
        ({"id": "u1", "email": LOGIN["email"], "confirmation_sent_at": "2026-11-09"}, None),
    ],
    ids=["logged_in", "confirm_email_first"],
)
def test_signup(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    answer: dict[str, Any],
    expected: dict[str, str] | None,
) -> None:
    calls = fake_supabase(monkeypatch, 200, answer)
    res = client.post("/auth/signup", json=LOGIN)
    assert res.status_code == 201
    assert res.json() == expected
    assert calls[0].url.path == "/auth/v1/signup"


def test_invalid_refresh_token_is_401(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_supabase(monkeypatch, 400, {"error_code": "validation_failed"})
    assert client.post("/auth/refresh", json={"refresh_token": "old"}).status_code == 401
