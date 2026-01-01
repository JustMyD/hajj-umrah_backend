from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import select, update, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.entities.auth_identity import AuthIdentity
from src.core.auth.entities.magic_link_token import MagicLinkToken
from src.core.auth.entities.refresh_token import RefreshToken
from src.core.auth.ports.auth_identity_repository import AuthIdentityRepository
from src.core.auth.ports.magic_link_repository import MagicLinkRepository
from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.db.models.auth import AuthIdentities, MagicLinkTokens, RefreshTokens
from src.infrastructure.auth.magic_tokens import hash_token


def _identity_to_entity(model: AuthIdentities) -> AuthIdentity:
    return AuthIdentity(
        id=model.id,
        user_id=model.user_id,
        provider=model.provider,
        provider_account_id=model.provider_account_id,
        email_at_provider=model.email_at_provider,
        email_verified=model.email_verified,
        created_at=model.created_at,
    )


def _magic_to_entity(model: MagicLinkTokens) -> MagicLinkToken:
    return MagicLinkToken(
        id=model.id,
        email=model.email,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        created_at=model.created_at,
        used_at=model.used_at,
        request_ip=model.request_ip,
        user_agent=model.user_agent,
    )


class SqlAlchemyAuthIdentityRepository(AuthIdentityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_account(self, *, provider: str, provider_account_id: str) -> AuthIdentity | None:
        res = await self.session.execute(
            select(AuthIdentities).where(
                and_(
                    AuthIdentities.provider == provider,
                    AuthIdentities.provider_account_id == provider_account_id,
                )
            )
        )
        model = res.scalar_one_or_none()
        return _identity_to_entity(model) if model else None

    async def create(self, identity: AuthIdentity) -> AuthIdentity:
        model = AuthIdentities(
            id=identity.id,
            user_id=identity.user_id,
            provider=identity.provider,
            provider_account_id=identity.provider_account_id,
            email_at_provider=identity.email_at_provider,
            email_verified=identity.email_verified,
            created_at=identity.created_at or datetime.now(timezone.utc),
        )
        self.session.add(model)
        await self.session.flush()
        return _identity_to_entity(model)


class SqlAlchemyMagicLinkRepository(MagicLinkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_recent_requests(self, *, email: str, since: datetime) -> int:
        res = await self.session.execute(
            select(func.count(MagicLinkTokens.id)).where(
                and_(MagicLinkTokens.email == email, MagicLinkTokens.created_at >= since)
            )
        )
        return int(res.scalar_one())

    async def create_token(self, token: MagicLinkToken) -> MagicLinkToken:
        model = MagicLinkTokens(
            id=token.id,
            email=token.email,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            created_at=token.created_at or datetime.now(timezone.utc),
            used_at=token.used_at,
            request_ip=token.request_ip,
            user_agent=token.user_agent,
        )
        self.session.add(model)
        await self.session.commit()
        return _magic_to_entity(model)

    async def consume_token(self, *, email: str, token_hash: str, now: datetime) -> MagicLinkToken | None:
        # атомарная "пометка used_at" через UPDATE ... WHERE used_at IS NULL AND expires_at >= now
        res = await self.session.execute(
            update(MagicLinkTokens)
            .where(
                and_(
                    MagicLinkTokens.email == email,
                    MagicLinkTokens.token_hash == token_hash,
                    MagicLinkTokens.used_at.is_(None),
                    MagicLinkTokens.expires_at >= now,
                )
            )
            .values(used_at=now)
            .returning(MagicLinkTokens)
        )
        model = res.scalar_one_or_none()
        await self.session.commit()
        return _magic_to_entity(model) if model else None


def _refresh_to_entity(model: RefreshTokens) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        created_at=model.created_at,
        used_at=model.used_at,
        request_ip=model.request_ip,
        user_agent=model.user_agent,
    )


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        model = RefreshTokens(
            id=token.id,
            user_id=token.user_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            created_at=token.created_at or datetime.now(timezone.utc),
            used_at=token.used_at,
            request_ip=token.request_ip,
            user_agent=token.user_agent,
        )
        self.session.add(model)
        await self.session.flush()
        return _refresh_to_entity(model)

    async def get_by_token_hash(self, *, token_hash: str) -> RefreshToken | None:
        res = await self.session.execute(
            select(RefreshTokens).where(RefreshTokens.token_hash == token_hash)
        )
        model = res.scalar_one_or_none()
        return _refresh_to_entity(model) if model else None

    async def consume_token(self, *, token_hash: str, now: datetime) -> RefreshToken | None:
        # Атомарная "пометка used_at" через UPDATE ... WHERE used_at IS NULL AND expires_at >= now
        res = await self.session.execute(
            update(RefreshTokens)
            .where(
                and_(
                    RefreshTokens.token_hash == token_hash,
                    RefreshTokens.used_at.is_(None),
                    RefreshTokens.expires_at >= now,
                )
            )
            .values(used_at=now)
            .returning(RefreshTokens)
        )
        model = res.scalar_one_or_none()
        await self.session.flush()
        return _refresh_to_entity(model) if model else None

    async def revoke_all_for_user(self, *, user_id: UUID, now: datetime) -> int:
        # Пометить все активные токены пользователя как использованные
        res = await self.session.execute(
            update(RefreshTokens)
            .where(
                and_(
                    RefreshTokens.user_id == user_id,
                    RefreshTokens.used_at.is_(None),
                    RefreshTokens.expires_at >= now,
                )
            )
            .values(used_at=now)
        )
        return res.rowcount or 0

    async def revoke_token_by_hash(self, *, token_hash: str, now: datetime) -> bool:
        # Пометить конкретный токен как использованный
        res = await self.session.execute(
            update(RefreshTokens)
            .where(
                and_(
                    RefreshTokens.token_hash == token_hash,
                    RefreshTokens.used_at.is_(None),
                    RefreshTokens.expires_at >= now,
                )
            )
            .values(used_at=now)
        )
        return res.rowcount > 0

    async def delete_expired(self, *, now: datetime) -> int:
        # Удалить истёкшие токены
        res = await self.session.execute(
            delete(RefreshTokens).where(RefreshTokens.expires_at < now)
        )
        await self.session.commit()
        return res.rowcount or 0

    async def create_from_raw_token(
        self,
        *,
        raw_token: str,
        user_id: UUID,
        token_pepper: str,
        expires_at: datetime,
        request_ip: str | None = None,
        user_agent: str | None = None,
        created_at: datetime | None = None,
    ) -> RefreshToken:
        """Создать refresh токен из сырого токена (хеширует и сохраняет)."""
        token_hash = hash_token(token=raw_token, pepper=token_pepper)
        token_entity = RefreshToken(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=created_at or datetime.now(timezone.utc),
            used_at=None,
            request_ip=request_ip,
            user_agent=user_agent,
        )
        return await self.create(token_entity)


