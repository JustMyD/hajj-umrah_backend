from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.core.auth.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshToken:
        """Создать новый refresh токен."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_token_hash(self, *, token_hash: str) -> RefreshToken | None:
        """Найти refresh токен по хешу."""
        raise NotImplementedError

    @abstractmethod
    async def consume_token(self, *, token_hash: str, now: datetime) -> RefreshToken | None:
        """
        Атомарно пометить токен как использованный.
        Возвращает токен, если он был успешно помечен, иначе None.
        """
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_for_user(self, *, user_id: UUID, now: datetime) -> int:
        """
        Отозвать все активные refresh токены пользователя (пометить used_at).
        Возвращает количество отозванных токенов.
        """
        raise NotImplementedError

    @abstractmethod
    async def revoke_token_by_hash(self, *, token_hash: str, now: datetime) -> bool:
        """
        Отозвать конкретный refresh токен по его хешу (пометить used_at).
        Возвращает True если токен был успешно отозван, False если токен не найден или уже использован.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_expired(self, *, now: datetime) -> int:
        """
        Удалить истёкшие токены (expires_at < now).
        Возвращает количество удалённых токенов.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_from_raw_token(
        self,
        *,
        raw_token: str,
        user_id: UUID,
        token_pepper: str,
        expires_at: datetime,
        request_ip: str | None = None,
        user_agent: str | None = None,
        created_at: datetime | None = None,
    ) -> RefreshToken:
        """
        Создать refresh токен из сырого токена (хеширует и сохраняет).
        Удобный метод для создания токена из use cases.
        """
        raise NotImplementedError

