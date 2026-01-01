from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from src.core.auth.entities.magic_link_token import MagicLinkToken
from src.core.auth.ports.email_sender import EmailSender
from src.core.auth.ports.magic_link_repository import MagicLinkRepository


@dataclass(frozen=True)
class MagicStartResult:
    ok: bool = True


class MagicStartUseCase:
    def __init__(
        self,
        *,
        magic_repo: MagicLinkRepository,
        email_sender: EmailSender,
        token_ttl_minutes: int,
        rate_limit_per_hour: int,
        frontend_base_url: str,
    ) -> None:
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
    ) -> MagicStartResult:
        now = now or datetime.utcnow()
        since = now - timedelta(hours=1)
        recent = await self.magic_repo.count_recent_requests(email=email, since=since)
        if recent >= self.rate_limit_per_hour:
            # не раскрываем детали, чтобы не помогать злоумышленнику
            return MagicStartResult(ok=True)

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
        return MagicStartResult(ok=True)


