from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.core.auth.entities.magic_link_token import MagicLinkToken


class MagicLinkRepository(ABC):
    @abstractmethod
    async def count_recent_requests(self, *, email: str, since: datetime) -> int:
        raise NotImplementedError

    @abstractmethod
    async def create_token(self, token: MagicLinkToken) -> MagicLinkToken:
        raise NotImplementedError

    @abstractmethod
    async def consume_token(self, *, email: str, token_hash: str, now: datetime) -> MagicLinkToken | None:
        """
        Вернуть токен и пометить used_at если он валиден (не истёк и не использован).
        """
        raise NotImplementedError


