from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from distutils.util import execute

from src.core.user.entities.user import User
from src.core.user.ports.email_change_repository import EmailChangeRepository
from src.core.user.ports.user_repository import UserRepository
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailChangeConfirmResult:
    user: User


class EmailChangeConfirmUseCase(UseCase):
    def __init__(self, *, repo: EmailChangeRepository, user_repo: UserRepository, uow: UnitOfWork) -> None:
        super().__init__(uow)
        self.email_change_repo = repo
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
        try:
            now = now or datetime.now(timezone.utc)
            new_email = await self.email_change_repo.consume_token(user_id=user.id, token_hash=token_hash, now=now)
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
            await self.uow.commit()
            return EmailChangeConfirmResult(user=user)
        except Exception as e:
            await self.uow.rollback()
            raise e
