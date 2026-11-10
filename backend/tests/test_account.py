"""Parent account: the PIN for the parent area."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Guardian
from tests.conftest import PARENT, bearer

OTHER = "22222222-2222-2222-2222-222222222222"


def check(client: TestClient, pin: str, headers: dict[str, str] | None = None) -> bool:
    res = client.post("/account/pin/check", json={"pin": pin}, headers=headers)
    return res.json()["correct"]


def test_new_parent_has_no_pin(client: TestClient) -> None:
    assert client.get("/account").json() == {"pin_set": False}
    assert not check(client, "1234")


def test_pin_opens_the_parent_area(client: TestClient) -> None:
    assert client.put("/account/pin", json={"pin": "4711"}).json() == {"pin_set": True}
    assert client.get("/account").json() == {"pin_set": True}
    assert check(client, "4711")
    assert not check(client, "1234")


def test_pin_is_stored_salted(client: TestClient, db: sessionmaker[Session]) -> None:
    client.put("/account/pin", json={"pin": "4711"})
    client.put("/account/pin", json={"pin": "4711"}, headers=bearer(OTHER))
    with db() as session:
        mine, theirs = (session.get(Guardian, g).pin_hash for g in (PARENT, OTHER))
    assert mine != theirs
    assert "4711" not in (mine, theirs)


def test_pin_belongs_to_one_parent(client: TestClient) -> None:
    client.put("/account/pin", json={"pin": "4711"})
    other = bearer(OTHER)
    assert client.get("/account", headers=other).json() == {"pin_set": False}
    assert not check(client, "4711", headers=other)


@pytest.mark.parametrize("pin", ["", "123", "12345", "12a4", "١٢٣٤"])
def test_pin_has_four_digits(client: TestClient, pin: str) -> None:
    assert client.put("/account/pin", json={"pin": pin}).status_code == 422


def test_forgotten_pin_is_reset(client: TestClient) -> None:
    client.put("/account/pin", json={"pin": "4711"})
    assert client.delete("/account/pin").json() == {"pin_set": False}
    assert client.get("/account").json() == {"pin_set": False}
    assert not check(client, "4711")


def test_pin_before_first_child(client: TestClient) -> None:
    client.put("/account/pin", json={"pin": "4711"})
    assert client.post("/children", json={"name": "Lena", "sign": "fish"}).status_code == 201
    assert check(client, "4711")


def test_account_needs_a_token(client: TestClient) -> None:
    assert client.get("/account", headers={"Authorization": ""}).status_code == 401
