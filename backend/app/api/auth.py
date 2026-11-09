"""Parent accounts. FastAPI forwards login to Supabase Auth and checks its tokens.

The frontend never talks to Supabase. Moving to Keycloak changes only this module.
"""

from typing import Annotated, Any

import httpx2
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.settings import settings

ISSUER = f"{settings.supabase_url}/auth/v1"
gotrue = httpx2.Client(
    base_url=ISSUER, headers={"apikey": settings.supabase_publishable_key}, timeout=10
)
jwks = jwt.PyJWKClient(f"{ISSUER}/.well-known/jwks.json")
bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth")


class Credentials(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class SessionOut(BaseModel):
    access_token: str
    refresh_token: str


def forward(path: str, body: dict[str, str]) -> dict[str, Any]:
    """Call Supabase Auth. An error keeps its status and passes on the error code."""
    try:
        res = gotrue.post(path, json=body)
    except httpx2.HTTPError as e:
        raise HTTPException(502, "auth_unreachable") from e
    if res.is_success:
        return res.json()
    try:
        code = res.json()["error_code"]
    except (ValueError, KeyError):
        code = "auth_error"
    raise HTTPException(res.status_code, code)


@router.post("/signup", response_model=SessionOut | None, status_code=201)
def signup(body: Credentials) -> Any:
    """None: the account needs email confirmation first, then login."""
    data = forward("/signup", body.model_dump())
    return data if "access_token" in data else None


@router.post("/login", response_model=SessionOut)
def login(body: Credentials) -> Any:
    return forward("/token?grant_type=password", body.model_dump())


@router.post("/refresh", response_model=SessionOut)
def refresh(body: RefreshIn) -> Any:
    """401 when the refresh token is no longer valid: the parent logs in again."""
    try:
        return forward("/token?grant_type=refresh_token", body.model_dump())
    except HTTPException as e:
        if e.status_code == 400:
            raise HTTPException(401, "session_expired") from e
        raise


def guardian_id(token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> str:
    """The parent's account ID from a valid access token."""
    if token is None:
        raise HTTPException(401, "not_logged_in")
    try:
        key = jwks.get_signing_key_from_jwt(token.credentials).key
        claims = jwt.decode(
            token.credentials,
            key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=ISSUER,
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWKClientConnectionError as e:
        raise HTTPException(503, "auth_unreachable") from e
    except jwt.PyJWTError as e:
        raise HTTPException(401, "invalid_token") from e
    return claims["sub"]


Parent = Annotated[str, Depends(guardian_id)]
