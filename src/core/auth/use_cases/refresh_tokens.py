from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.core.auth.use_cases.oauth_exchange import TokensPair
from src.infrastructure.auth.magic_tokens import hash_token


@dataclass(frozen=True)
class RefreshResult:
    user: User
    tokens: TokensPair


class RefreshTokensUseCase:
    def __init__(
        self,
        *,
        token_service: TokenService,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        refresh_token_pepper: str,
        refresh_ttl_days: int,
    ) -> None:
        self.token_service = token_service
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.refresh_token_pepper = refresh_token_pepper
        self.refresh_ttl_days = refresh_ttl_days

    async def execute(
        self,
        *,
        refresh_token: str,
        request_ip: str | None = None,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> RefreshResult:
        try:
            now = now or datetime.now(timezone.utc)
            
            # Проверяем JWT токен
            user_id = self.token_service.verify_refresh_token(refresh_token)
            
            # Хешируем токен для поиска в БД
            token_hash = hash_token(token=refresh_token, pepper=self.refresh_token_pepper)
            
            # Атомарно помечаем старый токен как использованный
            old_token = await self.refresh_token_repo.consume_token(token_hash=token_hash, now=now)
            if old_token is None:
                raise ValueError("invalid or expired refresh token")
            
            # Проверяем, что токен принадлежит правильному пользователю
            if old_token.user_id != user_id:
                raise ValueError("token user mismatch")
            
            user = await self.user_repo.get_by_id(user_id)
            if user is None:
                raise ValueError("user not found")
            
            # Выдаём новые токены
            new_access_token = self.token_service.issue_access_token(user_id=user.id)
            new_refresh_token = self.token_service.issue_refresh_token(user_id=user.id)
            
            # Сохраняем новый refresh токен в БД
            await self.refresh_token_repo.create_from_raw_token(
                raw_token=new_refresh_token,
                user_id=user.id,
                token_pepper=self.refresh_token_pepper,
                expires_at=now + timedelta(days=self.refresh_ttl_days),
                request_ip=request_ip,
                user_agent=user_agent,
                created_at=now,  # Используем timezone-aware UTC datetime для корректного времени создания
            )
            await self.refresh_token_repo.session.commit()
        
        except Exception as e:
            await self.refresh_token_repo.session.rollback()
            raise e
        
        tokens = TokensPair(access=new_access_token, refresh=new_refresh_token)
        return RefreshResult(user=user, tokens=tokens)


