from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class EmailChangeRepository(ABC):
    @abstractmethod
    async def count_recent_requests(self, *, user_id: UUID, since: datetime) -> int:
        raise NotImplementedError

    @abstractmethod
    async def create_token(
        self,
        *,
        token_id: UUID,
        user_id: UUID,
        new_email: str,
        token_hash: str,
        expires_at: datetime,
        request_ip: str | None = None,
        user_agent: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consume_token(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        now: datetime,
    ) -> str | None:
        """
        Вернуть new_email и пометить used_at если токен валиден (не истёк и не использован).
        """
        raise NotImplementedError


