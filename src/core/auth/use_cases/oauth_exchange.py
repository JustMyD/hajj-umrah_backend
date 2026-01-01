from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.core.auth.entities.auth_identity import AuthIdentity
from src.core.auth.ports.auth_identity_repository import AuthIdentityRepository
from src.core.auth.ports.oauth_validator import OAuthValidator
from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository


@dataclass(frozen=True)
class TokensPair:
    access: str
    refresh: str


@dataclass(frozen=True)
class AuthResult:
    user: User
    tokens: TokensPair
    provider: str
    provider_account_id: str
    required_actions: list[str]
    suggested_email: str | None = None


class OAuthExchangeUseCase:
    def __init__(
        self,
        *,
        oauth_validator: OAuthValidator,
        identity_repo: AuthIdentityRepository,
        user_repo: UserRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        refresh_token_pepper: str,
        refresh_ttl_days: int,
    ) -> None:
        self.oauth_validator = oauth_validator
        self.identity_repo = identity_repo
        self.user_repo = user_repo
        self.token_service = token_service
        self.refresh_token_repo = refresh_token_repo
        self.refresh_token_pepper = refresh_token_pepper
        self.refresh_ttl_days = refresh_ttl_days

    async def execute(
        self,
        *,
        provider: str,
        access_token: str,
        id_token: str | None = None,
        request_ip: str | None = None,
        user_agent: str | None = None,
    ) -> AuthResult:
        try:
            profile = await self.oauth_validator.validate(provider=provider, access_token=access_token, id_token=id_token)

            identity = await self.identity_repo.get_by_provider_account(
                provider=profile.provider,
                provider_account_id=profile.provider_account_id,
            )
            if identity is None:
                # минимальный linking: если есть подтверждённый email — пробуем найти user по email
                user: User | None = None
                if profile.email and (profile.email_verified is True):
                    user = await self.user_repo.get_by_email(profile.email)
                if user is None:
                    user = await self.user_repo.create(User(id=uuid4(), email=profile.email, name=profile.full_name))
                identity = await self.identity_repo.create(
                    AuthIdentity(
                        id=uuid4(),
                        user_id=user.id,
                        provider=profile.provider,
                        provider_account_id=profile.provider_account_id,
                        email_at_provider=profile.email,
                        email_verified=profile.email_verified,
                    )
                )
            else:
                user = await self.user_repo.get_by_id(identity.user_id)
                if user is None:
                    # состояние БД повреждено — identity есть, user нет
                    raise RuntimeError("auth identity points to missing user")

            now = datetime.now(timezone.utc)

            # Если провайдер вернул подтверждённый email — можем заполнить и сразу отметить verified_at.
            if profile.email and (profile.email_verified is True) and (user.email != profile.email or user.email_verified_at is None):
                user.email = profile.email
                user.email_verified_at = now
                user = await self.user_repo.update(user)

            required_actions: list[str] = []
            if user.email is None:
                required_actions.append("add_email")
            elif user.email_verified_at is None:
                required_actions.append("verify_email")

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
        except Exception as e:
            await self.refresh_token_repo.session.rollback()
            raise e
        
        suggested_email = None
        # suggested_email заполним на уровне роутера через email_hint,
        # но если провайдер сам дал email (необязательно verified) — тоже можно подсказать.
        if user.email is None and profile.email:
            suggested_email = profile.email
        return AuthResult(
            user=user,
            tokens=tokens,
            provider=profile.provider,
            provider_account_id=profile.provider_account_id,
            required_actions=required_actions,
            suggested_email=suggested_email,
        )


