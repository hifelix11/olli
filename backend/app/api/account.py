"""The parent account: the PIN for the parent area.

The PIN keeps the child out of the parent area. It is no login: the access token is.
Only a salted hash is stored. Parents may reuse a bank card PIN.
"""

import hashlib
import hmac
import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import Parent
from app.db.models import Guardian
from app.db.session import get_session

ROUNDS = 100_000

router = APIRouter(prefix="/account")
Db = Annotated[Session, Depends(get_session)]


class PinIn(BaseModel):
    pin: str = Field(pattern=r"^[0-9]{4}$")


class AccountOut(BaseModel):
    pin_set: bool


class PinCheckOut(BaseModel):
    correct: bool


def guardian(session: Session, parent: str) -> Guardian:
    """The parent's row. Created on first use."""
    row = session.get(Guardian, parent)
    if row is None:
        row = Guardian(id=parent)
        session.add(row)
        session.flush()
    return row


def digest(pin: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, ROUNDS).hex()


@router.get("", response_model=AccountOut)
def account(session: Db, parent: Parent) -> Any:
    """pin_set false: the app asks for a PIN first."""
    row = session.get(Guardian, parent)
    return AccountOut(pin_set=row is not None and row.pin_hash is not None)


@router.put("/pin", response_model=AccountOut)
def set_pin(body: PinIn, session: Db, parent: Parent) -> Any:
    salt = os.urandom(16)
    guardian(session, parent).pin_hash = f"{salt.hex()}:{digest(body.pin, salt)}"
    return AccountOut(pin_set=True)


@router.post("/pin/check", response_model=PinCheckOut)
def check_pin(body: PinIn, session: Db, parent: Parent) -> Any:
    row = session.get(Guardian, parent)
    if row is None or row.pin_hash is None:
        return PinCheckOut(correct=False)
    salt, expected = row.pin_hash.split(":")
    return PinCheckOut(correct=hmac.compare_digest(digest(body.pin, bytes.fromhex(salt)), expected))


@router.delete("/pin", response_model=AccountOut)
def reset_pin(session: Db, parent: Parent) -> Any:
    """Forgotten PIN. The app logs out next. After login with the password, a new PIN follows."""
    row = session.get(Guardian, parent)
    if row is not None:
        row.pin_hash = None
    return AccountOut(pin_set=False)
