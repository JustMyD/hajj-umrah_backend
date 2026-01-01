from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str | None = None
    email_verified_at: datetime | None = None
    name: str | None = None
    surname: str | None = None
    phone: str | None = None
    city: str | None = None
    birth_date: date | None = None
    email_notification: bool = True
    sms_notification: bool = True
    favorite_tour_ids: List[UUID] = field(default_factory=list)
    comparison_tour_ids: List[UUID] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None