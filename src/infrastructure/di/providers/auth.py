from dishka import Provider, provide, Scope
from dynaconf import Dynaconf
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.ports.auth_identity_repository import AuthIdentityRepository
from src.core.auth.ports.email_sender import EmailSender
from src.core.auth.ports.magic_link_repository import MagicLinkRepository
from src.core.auth.ports.oauth_validator import OAuthValidator
from src.core.auth.ports.refresh_token_repository import RefreshTokenRepository
from src.core.auth.ports.token_service import TokenService
from src.core.auth.use_cases.dev_login import DevLoginUseCase
from src.core.auth.use_cases.logout import LogoutUseCase
from src.core.auth.use_cases.magic_start import MagicStartUseCase
from src.core.auth.use_cases.magic_verify import MagicVerifyUseCase
from src.core.auth.use_cases.oauth_exchange import OAuthExchangeUseCase
from src.core.auth.use_cases.refresh_tokens import RefreshTokensUseCase
from src.core.user.ports.user_repository import UserRepository
from src.core.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.jwt_token_service import JoseJWTTokenService
from src.infrastructure.auth.oauth_validator import HttpxOAuthValidator
from src.infrastructure.db.repositories.auth_repo import (
    SqlAlchemyAuthIdentityRepository,
    SqlAlchemyMagicLinkRepository,
    SqlAlchemyRefreshTokenRepository,
)
from src.infrastructure.email.smtp_email_sender import SmtpEmailSender
from src.infrastructure.common.db_unit_of_work import SqlAlchemyUnitOfWork


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_auth_identity_repo(self, session: AsyncSession) -> AuthIdentityRepository:
        return SqlAlchemyAuthIdentityRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_magic_repo(self, session: AsyncSession) -> MagicLinkRepository:
        return SqlAlchemyMagicLinkRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_refresh_token_repo(self, session: AsyncSession) -> RefreshTokenRepository:
        return SqlAlchemyRefreshTokenRepository(session)

    @provide(scope=Scope.APP)
    def provide_token_service(self, settings: Dynaconf) -> TokenService:
        return JoseJWTTokenService(
            secret=str(settings.AUTH_JWT_SECRET),
            issuer=str(settings.AUTH_JWT_ISSUER),
            access_ttl_minutes=int(settings.AUTH_ACCESS_TTL_MINUTES),
            refresh_ttl_days=int(settings.AUTH_REFRESH_TTL_DAYS),
        )

    @provide(scope=Scope.APP)
    def provide_oauth_validator(self) -> OAuthValidator:
        return HttpxOAuthValidator()

    @provide(scope=Scope.APP)
    def provide_email_sender(self, settings: Dynaconf) -> EmailSender:
        return SmtpEmailSender(
            host=str(settings.SMTP_HOST),
            port=int(settings.SMTP_PORT),
            user=str(settings.SMTP_USER),
            password=str(settings.SMTP_PASSWORD),
            sender_from=str(settings.SMTP_FROM),
        )

    @provide(scope=Scope.REQUEST)
    def provide_oauth_exchange_use_case(
        self,
        oauth_validator: OAuthValidator,
        identity_repo: AuthIdentityRepository,
        user_repo: UserRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        settings: Dynaconf,
    ) -> OAuthExchangeUseCase:
        return OAuthExchangeUseCase(
            oauth_validator=oauth_validator,
            identity_repo=identity_repo,
            user_repo=user_repo,
            token_service=token_service,
            refresh_token_repo=refresh_token_repo,
            refresh_token_pepper=str(settings.AUTH_REFRESH_TOKEN_PEPPER),
            refresh_ttl_days=int(settings.AUTH_REFRESH_TTL_DAYS),
        )

    @provide(scope=Scope.REQUEST)
    def provide_magic_start_use_case(
        self,
        magic_repo: MagicLinkRepository,
        email_sender: EmailSender,
        settings: Dynaconf,
    ) -> MagicStartUseCase:
        return MagicStartUseCase(
            magic_repo=magic_repo,
            email_sender=email_sender,
            token_ttl_minutes=int(settings.AUTH_MAGIC_TOKEN_TTL_MINUTES),
            rate_limit_per_hour=int(settings.AUTH_MAGIC_RATE_LIMIT_PER_HOUR),
            frontend_base_url=str(settings.FRONTEND_BASE_URL),
        )

    @provide(scope=Scope.REQUEST)
    def provide_magic_verify_use_case(
        self,
        magic_repo: MagicLinkRepository,
        identity_repo: AuthIdentityRepository,
        user_repo: UserRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        settings: Dynaconf,
    ) -> MagicVerifyUseCase:
        return MagicVerifyUseCase(
            magic_repo=magic_repo,
            identity_repo=identity_repo,
            user_repo=user_repo,
            token_service=token_service,
            refresh_token_repo=refresh_token_repo,
            refresh_token_pepper=str(settings.AUTH_REFRESH_TOKEN_PEPPER),
            refresh_ttl_days=int(settings.AUTH_REFRESH_TTL_DAYS),
        )

    @provide(scope=Scope.REQUEST)
    def provide_refresh_tokens_use_case(
        self,
        token_service: TokenService,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        settings: Dynaconf,
    ) -> RefreshTokensUseCase:
        return RefreshTokensUseCase(
            token_service=token_service,
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
            refresh_token_pepper=str(settings.AUTH_REFRESH_TOKEN_PEPPER),
            refresh_ttl_days=int(settings.AUTH_REFRESH_TTL_DAYS),
        )

    @provide(scope=Scope.REQUEST)
    def provide_dev_login_use_case(
        self,
        user_repo: UserRepository,
        identity_repo: AuthIdentityRepository,
        token_service: TokenService,
        refresh_token_repo: RefreshTokenRepository,
        settings: Dynaconf,
        uow: UnitOfWork,
    ) -> DevLoginUseCase:
        env = str(settings.get("ENV_FOR_DYNACONF", "default")).lower()
        is_dev = env in ("development", "dev", "local")
        default_email = str(settings.get("DEV_DEFAULT_EMAIL", "dev@test.local"))
        return DevLoginUseCase(
            user_repo=user_repo,
            identity_repo=identity_repo,
            token_service=token_service,
            refresh_token_repo=refresh_token_repo,
            refresh_token_pepper=str(settings.AUTH_REFRESH_TOKEN_PEPPER),
            refresh_ttl_days=int(settings.AUTH_REFRESH_TTL_DAYS),
            default_dev_email=default_email,
            is_dev_mode=is_dev,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def provide_logout_use_case(
        self,
        refresh_token_repo: RefreshTokenRepository,
        token_service: TokenService,
        sqlalchemy_uow: UnitOfWork,
        settings: Dynaconf,
    ) -> LogoutUseCase:
        return LogoutUseCase(
            refresh_token_repo=refresh_token_repo,
            token_service=token_service,
            refresh_token_pepper=str(settings.AUTH_REFRESH_TOKEN_PEPPER),
            uow=sqlalchemy_uow
        )


