from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from src.core.user.entities.user import User
from src.core.user.ports.email_change_repository import EmailChangeRepository
from src.core.user.ports.user_repository import UserRepository


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailChangeConfirmResult:
    user: User


class EmailChangeConfirmUseCase:
    def __init__(self, *, repo: EmailChangeRepository, user_repo: UserRepository) -> None:
        self.repo = repo
        self.user_repo = user_repo

    async def execute(
        self,
        *,
        user: User,
        token_hash: str,
        request_ip: str | None = None,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> EmailChangeConfirmResult:
        now = now or datetime.utcnow()
        new_email = await self.repo.consume_token(user_id=user.id, token_hash=token_hash, now=now)
        if new_email is None:
            raise ValueError("invalid or expired token")

        # Проверяем, что email не занят другим пользователем (race condition protection)
        existing_user = await self.user_repo.get_by_email(new_email)
        if existing_user is not None and existing_user.id != user.id:
            raise ValueError("email already taken")

        old_email = user.email
        user.email = new_email
        user.email_verified_at = now
        user = await self.user_repo.update(user)

        logger.info(
            "email_change_confirmed user_id=%s old_email=%s new_email=%s request_ip=%s user_agent=%s",
            user.id,
            old_email,
            new_email,
            request_ip,
            user_agent,
        )
        return EmailChangeConfirmResult(user=user)


