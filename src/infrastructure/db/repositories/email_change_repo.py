from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.user.ports.email_change_repository import EmailChangeRepository
from src.infrastructure.db.models.auth import EmailChangeTokens


class SqlAlchemyEmailChangeRepository(EmailChangeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_recent_requests(self, *, user_id: UUID, since: datetime) -> int:
        res = await self.session.execute(
            select(func.count(EmailChangeTokens.id)).where(
                and_(EmailChangeTokens.user_id == user_id, EmailChangeTokens.created_at >= since)
            )
        )
        return int(res.scalar_one())

    async def create_token(
        self,
        *,
        token_id: UUID,
        user_id: UUID,
        new_email: str,
        token_hash: str,
        expires_at: datetime,
        request_ip: str | None = None,
        user_agent: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        model = EmailChangeTokens(
            id=token_id,
            user_id=user_id,
            new_email=new_email,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=created_at or datetime.now(timezone.utc),
            request_ip=request_ip,
            user_agent=user_agent,
        )
        self.session.add(model)
        await self.session.flush()

    async def consume_token(self, *, user_id: UUID, token_hash: str, now: datetime) -> str | None:
        res = await self.session.execute(
            update(EmailChangeTokens)
            .where(
                and_(
                    EmailChangeTokens.user_id == user_id,
                    EmailChangeTokens.token_hash == token_hash,
                    EmailChangeTokens.used_at.is_(None),
                    EmailChangeTokens.expires_at >= now,
                )
            )
            .values(used_at=now)
            .returning(EmailChangeTokens.new_email)
        )
        new_email = res.scalar_one_or_none()
        await self.session.flush()
        return str(new_email) if new_email else None


