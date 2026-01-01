from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.auth.entities.auth_identity import AuthIdentity


class AuthIdentityRepository(ABC):
    @abstractmethod
    async def get_by_provider_account(self, *, provider: str, provider_account_id: str) -> AuthIdentity | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, identity: AuthIdentity) -> AuthIdentity:
        raise NotImplementedError


