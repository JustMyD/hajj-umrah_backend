from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt
from jose.exceptions import JWTError

from src.core.auth.ports.token_service import TokenService


class TokenError(ValueError):
    pass


class JoseJWTTokenService(TokenService):
    def __init__(
        self,
        *,
        secret: str,
        issuer: str,
        access_ttl_minutes: int,
        refresh_ttl_days: int,
    ) -> None:
        self.secret = secret
        self.issuer = issuer
        self.access_ttl_minutes = access_ttl_minutes
        self.refresh_ttl_days = refresh_ttl_days
        self.algorithm = "HS256"

    def issue_access_token(self, *, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "typ": "access",
            "iss": self.issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.access_ttl_minutes)).timestamp()),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def issue_refresh_token(self, *, user_id: UUID) -> str:
        # Используем timezone-aware UTC datetime для корректного timestamp
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "typ": "refresh",
            "iss": self.issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=self.refresh_ttl_days)).timestamp()),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm], issuer=self.issuer)
        except JWTError as e:
            raise TokenError("invalid token") from e
        if payload.get("typ") != "access":
            raise TokenError("invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise TokenError("missing sub")
        try:
            return UUID(sub)
        except ValueError as e:
            raise TokenError("invalid sub") from e

    def verify_refresh_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm], issuer=self.issuer)
        except JWTError as e:
            raise TokenError("invalid token") from e
        if payload.get("typ") != "refresh":
            raise TokenError("invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise TokenError("missing sub")
        try:
            return UUID(sub)
        except ValueError as e:
            raise TokenError("invalid sub") from e


