from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.interfaces.http.models.user_model import UserResponse


class OAuthExchangeRequest(BaseModel):
    provider: Literal["google", "vk", "yandex"]
    access_token: str = Field(min_length=1)
    id_token: Optional[str] = None
    email_hint: Optional[str] = None


class MagicStartRequest(BaseModel):
    email: str = Field(min_length=3)


class MagicVerifyRequest(BaseModel):
    email: str = Field(min_length=3)
    token: str = Field(min_length=10)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokensResponse(BaseModel):
    access: str
    refresh: str


class AuthState(BaseModel):
    provider: str
    provider_account_id: str
    email: Optional[str] = None
    email_verified: bool = False


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokensResponse
    auth: Optional[AuthState] = None
    required_actions: list[str] = []
    suggested_email: Optional[str] = None


class MagicStartResponse(BaseModel):
    ok: bool = True


class DevLoginRequest(BaseModel):
    email: Optional[str] = Field(default=None, description="Email пользователя (опционально, по умолчанию используется DEV_DEFAULT_EMAIL)")


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=10, description="Refresh токен для отзыва")
