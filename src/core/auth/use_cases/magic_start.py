from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.core.auth.entities.magic_link_token import MagicLinkToken
from src.core.auth.ports.email_sender import EmailSender
from src.core.auth.ports.magic_link_repository import MagicLinkRepository
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork
from src.core.common.exceptions import RateLimitError


class MagicStartUseCase(UseCase):
    def __init__(
        self,
        *,
        magic_repo: MagicLinkRepository,
        email_sender: EmailSender,
        token_ttl_minutes: int,
        rate_limit_per_hour: int,
        frontend_base_url: str,
        uow: UnitOfWork,
    ) -> None:
        super().__init__(uow=uow)
        self.magic_repo = magic_repo
        self.email_sender = email_sender
        self.token_ttl_minutes = token_ttl_minutes
        self.rate_limit_per_hour = rate_limit_per_hour
        self.frontend_base_url = frontend_base_url.rstrip("/")

    async def execute(
        self,
        *,
        email: str,
        raw_token: str,
        token_hash: str,
        request_ip: str | None = None,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> None:
        try:
            now = now or datetime.now(timezone.utc)
            since = now - timedelta(hours=1)
            recent = await self.magic_repo.count_recent_requests(email=email, since=since)
            if recent >= self.rate_limit_per_hour:
                # не раскрываем детали, чтобы не помогать злоумышленнику
                raise RateLimitError("rate limit exceeded")

            expires_at = now + timedelta(minutes=self.token_ttl_minutes)
            await self.magic_repo.create_token(
                MagicLinkToken(
                    id=uuid4(),
                    email=email,
                    token_hash=token_hash,
                    expires_at=expires_at,
                    request_ip=request_ip,
                    user_agent=user_agent,
                )
            )

            # фронт ожидает /auth/magic?email=...&token=...
            magic_link_url = f"{self.frontend_base_url}/auth/magic?email={email}&token={raw_token}"
            await self.email_sender.send_magic_link(to_email=email, magic_link_url=magic_link_url)

            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            raise e
