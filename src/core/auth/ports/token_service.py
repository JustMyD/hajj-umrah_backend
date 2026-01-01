from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class TokenService(ABC):
    @abstractmethod
    def issue_access_token(self, *, user_id: UUID) -> str:
        raise NotImplementedError

    @abstractmethod
    def issue_refresh_token(self, *, user_id: UUID) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_access_token(self, token: str) -> UUID:
        """Вернуть user_id если токен валиден, иначе бросить исключение."""
        raise NotImplementedError

    @abstractmethod
    def verify_refresh_token(self, token: str) -> UUID:
        """Вернуть user_id если refresh-токен валиден, иначе бросить исключение."""
        raise NotImplementedError


