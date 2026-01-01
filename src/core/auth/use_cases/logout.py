from __future__ import annotations

from datetime import datetime, timezone

from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.magic_tokens import hash_token


class LogoutUseCase(UseCase):
    """Use case для выхода пользователя (отзыв конкретного refresh токена)."""

    def __init__(
        self,
        *,
        refresh_token_repo: RefreshTokenRepository,
        token_service: TokenService,
        refresh_token_pepper: str,
        uow: UnitOfWork,
    ) -> None:
        super().__init__(uow=uow)
        self.refresh_token_repo = refresh_token_repo
        self.token_service = token_service
        self.refresh_token_pepper = refresh_token_pepper

    async def execute(
        self,
        *,
        refresh_token: str,
        now: datetime | None = None,
    ) -> bool:
        """
        Отзывает конкретный refresh токен.
        Проверяет валидность токена и отзывает только его, не затрагивая другие устройства.
        
        Returns:
            True если токен был успешно отозван, False если токен невалидный, истёк или не найден.
        """
        try:
            now = now or datetime.now(timezone.utc)

            # Проверяем валидность refresh токена
            try:
                self.token_service.verify_refresh_token(refresh_token)
            except Exception as e:
                raise e

            # Хешируем токен для поиска в БД
            token_hash = hash_token(token=refresh_token, pepper=self.refresh_token_pepper)

            # Отзываем конкретный токен
            revoked = await self.refresh_token_repo.revoke_token_by_hash(token_hash=token_hash, now=now)
            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            raise e
        return revoked

