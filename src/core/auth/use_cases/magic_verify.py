from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from src.core.auth.entities.auth_identity import AuthIdentity
from src.core.auth.ports.auth_identity_repository import AuthIdentityRepository
from src.core.auth.ports.magic_link_repository import MagicLinkRepository
from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.core.auth.use_cases.oauth_exchange import TokensPair


@dataclass(frozen=True)
class MagicVerifyResult:
    user: User
    tokens: TokensPair


class MagicVerifyUseCase:
    def __init__(
        self,
        *,
        magic_repo: MagicLinkRepository,
        identity_repo: AuthIdentityRepository,
        user_repo: UserRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        refresh_token_pepper: str,
        refresh_ttl_days: int,
    ) -> None:
        self.magic_repo = magic_repo
        self.identity_repo = identity_repo
        self.user_repo = user_repo
        self.token_service = token_service
        self.refresh_token_repo = refresh_token_repo
        self.refresh_token_pepper = refresh_token_pepper
        self.refresh_ttl_days = refresh_ttl_days

    async def execute(
        self,
        *,
        email: str,
        token_hash: str,
        now: datetime | None = None,
        request_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MagicVerifyResult:
        try:
            now = now or datetime.now(timezone.utc)
            token = await self.magic_repo.consume_token(email=email, token_hash=token_hash, now=now)
            if token is None:
                raise ValueError("invalid or expired token")

            # provider_account_id=email
            identity = await self.identity_repo.get_by_provider_account(provider="email", provider_account_id=email)
            if identity is None:
                user = await self.user_repo.get_by_email(email)
                if user is None:
                    user = await self.user_repo.create(User(id=uuid4(), email=email))
                identity = await self.identity_repo.create(
                    AuthIdentity(
                        id=uuid4(),
                        user_id=user.id,
                        provider="email",
                        provider_account_id=email,
                        email_at_provider=email,
                        email_verified=True,
                    )
                )
            else:
                user = await self.user_repo.get_by_id(identity.user_id)
                if user is None:
                    raise RuntimeError("auth identity points to missing user")

            # Email подтверждён кликом по magic-link
            if user.email != email or user.email_verified_at is None:
                user.email = email
                user.email_verified_at = now
                user = await self.user_repo.update(user)

            tokens = TokensPair(
                access=self.token_service.issue_access_token(user_id=user.id),
                refresh=self.token_service.issue_refresh_token(user_id=user.id),
            )
            
            # Сохраняем refresh токен в БД
            await self.refresh_token_repo.create_from_raw_token(
                raw_token=tokens.refresh,
                user_id=user.id,
                token_pepper=self.refresh_token_pepper,
                expires_at=now + timedelta(days=self.refresh_ttl_days),
                request_ip=request_ip,
                user_agent=user_agent,
                created_at=now,
            )
            await self.refresh_token_repo.session.commit()
        except Exception as e:
            await self.refresh_token_repo.session.rollback()
            raise e
        
        return MagicVerifyResult(user=user, tokens=tokens)


