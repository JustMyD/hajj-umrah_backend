from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.core.auth.entities.auth_identity import AuthIdentity
from src.core.auth.ports.auth_identity_repository import AuthIdentityRepository
from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.auth.use_cases.oauth_exchange import AuthResult, TokensPair
from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.core.common.unit_of_work import UnitOfWork
from src.core.common.use_case import UseCase


class DevLoginUseCase(UseCase):
    """
    Use-case для dev-окружения: создаёт/находит пользователя и выдаёт токены без проверок.
    Работает только в development окружении.
    """

    def __init__(
        self,
        *,
        user_repo: UserRepository,
        identity_repo: AuthIdentityRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        refresh_token_pepper: str,
        refresh_ttl_days: int,
        default_dev_email: str,
        is_dev_mode: bool,
        uow: UnitOfWork,
    ) -> None:
        super().__init__(uow=uow)
        self.user_repo = user_repo
        self.identity_repo = identity_repo
        self.token_service = token_service
        self.refresh_token_repo = refresh_token_repo
        self.refresh_token_pepper = refresh_token_pepper
        self.refresh_ttl_days = refresh_ttl_days
        self.default_dev_email = default_dev_email
        self.is_dev_mode = is_dev_mode

    async def execute(
        self,
        *,
        email: str | None = None,
        request_ip: str | None = None,
        user_agent: str | None = None,
    ) -> AuthResult:
        try:
            if not self.is_dev_mode:
                raise RuntimeError("dev login is only available in development mode")

            target_email = email or self.default_dev_email
            if not target_email:
                raise ValueError("email is required")

            # Ищем пользователя по email
            user = await self.user_repo.get_by_email(target_email)
            if user is None:
                # Создаём нового dev-пользователя
                user = await self.user_repo.create(
                    User(
                        id=uuid4(),
                        email=target_email,
                        email_verified_at=datetime.now(timezone.utc),  # автоматически верифицируем для dev
                        name="Dev",
                        surname="User",
                    )
                )

            # Создаём/находим auth identity для dev провайдера
            identity = await self.identity_repo.get_by_provider_account(
                provider="dev",
                provider_account_id=target_email,
            )
            if identity is None:
                identity = await self.identity_repo.create(
                    AuthIdentity(
                        id=uuid4(),
                        user_id=user.id,
                        provider="dev",
                        provider_account_id=target_email,
                        email_at_provider=target_email,
                        email_verified=True,
                    )
                )

            tokens = TokensPair(
                access=self.token_service.issue_access_token(user_id=user.id),
                refresh=self.token_service.issue_refresh_token(user_id=user.id),
            )

            # Сохраняем refresh токен в БД
            now = datetime.now(timezone.utc)
            await self.refresh_token_repo.create_from_raw_token(
                raw_token=tokens.refresh,
                user_id=user.id,
                token_pepper=self.refresh_token_pepper,
                expires_at=now + timedelta(days=self.refresh_ttl_days),
                request_ip=request_ip,
                user_agent=user_agent,
                created_at=now,
            )

            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            raise e

        return AuthResult(
            user=user,
            tokens=tokens,
            provider="dev",
            provider_account_id=target_email,
            required_actions=[],
            suggested_email=None,
        )

