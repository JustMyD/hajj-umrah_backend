from __future__ import annotations

import secrets

from dynaconf import Dynaconf
from fastapi import APIRouter, HTTPException, Request
from dishka.integrations.fastapi import FromDishka, inject

from src.core.auth.use_cases.dev_login import DevLoginUseCase
from src.core.auth.use_cases.logout import LogoutUseCase
from src.core.auth.use_cases.magic_start import MagicStartUseCase
from src.core.auth.use_cases.magic_verify import MagicVerifyUseCase
from src.core.auth.use_cases.oauth_exchange import OAuthExchangeUseCase
from src.core.auth.use_cases.refresh_tokens import RefreshTokensUseCase
from src.infrastructure.auth.magic_tokens import hash_token
from src.interfaces.http.mappers.user_mapper import map_user_to_response
from src.interfaces.http.models.auth_model import (
    OAuthExchangeRequest,
    MagicStartRequest,
    MagicVerifyRequest,
    RefreshRequest,
    DevLoginRequest,
    LogoutRequest,
    AuthResponse,
    TokensResponse,
    MagicStartResponse,
    AuthState,
)


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/oauth/exchange", response_model=AuthResponse)
@inject
async def oauth_exchange(
    body: OAuthExchangeRequest,
    request: Request,
    use_case: FromDishka[OAuthExchangeUseCase],
) -> AuthResponse:
    try:
        result = await use_case.execute(
            provider=body.provider,
            access_token=body.access_token,
            id_token=body.id_token,
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    suggested_email = result.suggested_email
    if suggested_email is None and body.email_hint:
        suggested_email = body.email_hint

    return AuthResponse(
        user=map_user_to_response(result.user),
        tokens=TokensResponse(access=result.tokens.access, refresh=result.tokens.refresh),
        auth=AuthState(
            provider=result.provider,
            provider_account_id=result.provider_account_id,
            email=result.user.email,
            email_verified=bool(result.user.email_verified_at),
        ),
        required_actions=result.required_actions,
        suggested_email=suggested_email,
    )


@auth_router.post("/magic/start", response_model=MagicStartResponse)
@inject
async def magic_start(
    body: MagicStartRequest,
    request: Request,
    use_case: FromDishka[MagicStartUseCase],
    settings: FromDishka[Dynaconf],
) -> MagicStartResponse:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(token=raw_token, pepper=str(settings.AUTH_MAGIC_TOKEN_PEPPER))
    await use_case.execute(
        email=body.email,
        raw_token=raw_token,
        token_hash=token_hash,
        request_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    return MagicStartResponse(ok=True)


@auth_router.post("/magic/verify", response_model=AuthResponse)
@inject
async def magic_verify(
    body: MagicVerifyRequest,
    request: Request,
    use_case: FromDishka[MagicVerifyUseCase],
    settings: FromDishka[Dynaconf],
) -> AuthResponse:
    token_hash = hash_token(token=body.token, pepper=str(settings.AUTH_MAGIC_TOKEN_PEPPER))
    try:
        result = await use_case.execute(
            email=body.email,
            token_hash=token_hash,
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid or expired token") from exc
    return AuthResponse(
        user=map_user_to_response(result.user),
        tokens=TokensResponse(access=result.tokens.access, refresh=result.tokens.refresh),
    )


@auth_router.post("/refresh", response_model=AuthResponse)
@inject
async def refresh(
    body: RefreshRequest,
    request: Request,
    use_case: FromDishka[RefreshTokensUseCase],
) -> AuthResponse:
    try:
        result = await use_case.execute(
            refresh_token=body.refresh_token,
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    except Exception as e:
        raise
    return AuthResponse(
        user=map_user_to_response(result.user),
        tokens=TokensResponse(access=result.tokens.access, refresh=result.tokens.refresh),
    )


@auth_router.post("/dev/login", response_model=AuthResponse)
@inject
async def dev_login(
    body: DevLoginRequest,
    request: Request,
    use_case: FromDishka[DevLoginUseCase],
) -> AuthResponse:
    """
    Dev-only эндпоинт для быстрого получения токенов без email-верификации.
    Работает только в development окружении (ENV_FOR_DYNACONF=development).
    """
    try:
        result = await use_case.execute(
            email=body.email,
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AuthResponse(
        user=map_user_to_response(result.user),
        tokens=TokensResponse(access=result.tokens.access, refresh=result.tokens.refresh),
        auth=AuthState(
            provider=result.provider,
            provider_account_id=result.provider_account_id,
            email=result.user.email,
            email_verified=bool(result.user.email_verified_at),
        ),
        required_actions=result.required_actions,
        suggested_email=result.suggested_email,
    )


@auth_router.post("/logout")
@inject
async def logout(
    body: LogoutRequest,
    use_case: FromDishka[LogoutUseCase],
) -> dict[str, str]:
    """
    Выход пользователя - отзывает конкретный refresh токен.
    Не требует авторизации, так как использует refresh токен из body.
    """
    success = await use_case.execute(refresh_token=body.refresh_token)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired refresh token, or token already revoked"
        )
    return {"message": "Logged out successfully"}


