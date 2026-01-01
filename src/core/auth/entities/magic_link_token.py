from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MagicLinkToken:
    id: UUID
    email: str
    token_hash: str
    expires_at: datetime
    created_at: datetime | None = None
    used_at: datetime | None = None
    request_ip: str | None = None
    user_agent: str | None = None


