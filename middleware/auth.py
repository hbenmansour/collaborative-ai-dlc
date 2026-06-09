"""Cognito JWT validation middleware for FastAPI."""

from dataclasses import dataclass, field
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import settings

_bearer_scheme = HTTPBearer(auto_error=False)

# Cached JWKS
_jwks_cache: Optional[dict] = None


async def _get_jwks() -> dict:
    """Fetch and cache Cognito JWKS."""
    global _jwks_cache
    if _jwks_cache is None:
        url = (
            f"https://cognito-idp.{settings.cognito_region}.amazonaws.com"
            f"/{settings.cognito_user_pool_id}/.well-known/jwks.json"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def _find_key(token: str, jwks: dict) -> dict:
    """Find the matching JWK for the token's kid header."""
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find matching signing key",
    )


@dataclass
class CurrentUser:
    """Authenticated user extracted from Cognito JWT."""

    sub: str
    email: str = ""
    roles: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> CurrentUser:
    """Dependency that validates Cognito JWT and returns the current user.

    Extracts roles from cognito:groups claim and country access from
    custom:countries claim.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        jwks = await _get_jwks()
        key = _find_key(token, jwks)
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.cognito_app_client_id,
            issuer=(
                f"https://cognito-idp.{settings.cognito_region}.amazonaws.com"
                f"/{settings.cognito_user_pool_id}"
            ),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract roles from Cognito groups
    roles = payload.get("cognito:groups", [])
    if isinstance(roles, str):
        roles = [roles]

    # Extract country access from custom claim
    countries_raw = payload.get("custom:countries", "")
    countries = [c.strip() for c in countries_raw.split(",") if c.strip()] if countries_raw else []

    user = CurrentUser(
        sub=payload.get("sub", ""),
        email=payload.get("email", ""),
        roles=roles,
        countries=countries,
    )

    # Store on request state for downstream access
    request.state.current_user = user
    return user
