from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthProfile:
    provider: str
    provider_account_id: str
    email: str | None = None
    email_verified: bool | None = None
    full_name: str | None = None


