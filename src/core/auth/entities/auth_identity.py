from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AuthIdentity:
    id: UUID
    user_id: UUID
    provider: str
    provider_account_id: str
    email_at_provider: str | None = None
    email_verified: bool | None = None
    created_at: datetime | None = None


