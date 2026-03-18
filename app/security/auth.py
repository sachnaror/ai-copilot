from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings


@dataclass
class AuthUser:
    user_id: str
    roles: list[str]


bearer = HTTPBearer(auto_error=False)


def create_access_token(user_id: str, roles: list[str], expires_minutes: int | None = None) -> str:
    ttl = expires_minutes or settings.jwt_access_token_expire_minutes
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl)).timestamp()),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> AuthUser:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc

    user_id = payload.get("sub")
    roles = payload.get("roles", [])
    if not user_id or not isinstance(roles, list):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")
    return AuthUser(user_id=user_id, roles=[str(r) for r in roles])


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> AuthUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return _decode_token(credentials.credentials)


def require_roles(required_roles: list[str]):
    def _dependency(user: Annotated[AuthUser, Depends(get_current_user)]) -> AuthUser:
        if not set(required_roles).intersection(set(user.roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role missing. Need one of: {required_roles}",
            )
        return user

    return _dependency
