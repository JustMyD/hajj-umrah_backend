from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.auth.entities.oauth_profile import OAuthProfile


class OAuthValidator(ABC):
    @abstractmethod
    async def validate(self, *, provider: str, access_token: str, id_token: str | None = None) -> OAuthProfile:
        raise NotImplementedError


