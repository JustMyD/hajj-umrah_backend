from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from src.core.auth.ports.email_sender import EmailSender
from src.core.user.entities.user import User
from src.core.user.ports.email_change_repository import EmailChangeRepository
from src.core.user.ports.user_repository import UserRepository


@dataclass(frozen=True)
class EmailChangeStartResult:
    ok: bool = True


class EmailChangeStartUseCase:
    def __init__(
        self,
        *,
        repo: EmailChangeRepository,
        user_repo: UserRepository,
        email_sender: EmailSender,
        frontend_base_url: str,
        token_ttl_minutes: int,
        rate_limit_per_hour: int,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.email_sender = email_sender
        self.frontend_base_url = frontend_base_url.rstrip("/")
        self.token_ttl_minutes = token_ttl_minutes
        self.rate_limit_per_hour = rate_limit_per_hour

    async def execute(
        self,
        *,
        user: User,
        new_email: str,
        raw_token: str,
        token_hash: str,
        request_ip: str | None = None,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> EmailChangeStartResult:
        # Проверяем, что новый email не занят другим пользователем
        existing_user = await self.user_repo.get_by_email(new_email)
        if existing_user is not None and existing_user.id != user.id:
            raise ValueError("email already taken")
        
        # Проверяем, что пользователь не пытается установить тот же email
        if user.email == new_email:
            raise ValueError("new email must be different from current email")
        
        now = now or datetime.utcnow()
        since = now - timedelta(hours=1)
        recent = await self.repo.count_recent_requests(user_id=user.id, since=since)
        if recent >= self.rate_limit_per_hour:
            # не раскрываем детали
            return EmailChangeStartResult(ok=True)

        expires_at = now + timedelta(minutes=self.token_ttl_minutes)
        await self.repo.create_token(
            token_id=uuid4(),
            user_id=user.id,
            new_email=new_email,
            token_hash=token_hash,
            expires_at=expires_at,
            request_ip=request_ip,
            user_agent=user_agent,
            created_at=now,
        )

        url = f"{self.frontend_base_url}/auth/email-change?token={raw_token}"
        await self.email_sender.send_email_change_link(to_email=new_email, email_change_url=url)
        return EmailChangeStartResult(ok=True)


