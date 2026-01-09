from dishka import Provider, provide, Scope
from dynaconf import Dynaconf
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.ports.email_sender import EmailSender
from src.core.user.ports.email_change_repository import EmailChangeRepository
from src.core.user.ports.user_repository import UserRepository
from src.core.user.use_cases.email_change_confirm import EmailChangeConfirmUseCase
from src.core.user.use_cases.email_change_start import EmailChangeStartUseCase
from src.core.user.use_cases.update_me import UpdateMeUseCase
from src.core.user.use_cases.add_to_comparison import AddToComparisonUseCase
from src.core.user.use_cases.delete_from_comparison import DeleteFromComparisonUseCase
from src.core.user.use_cases.add_to_favorites import AddToFavoritesUseCase
from src.core.user.use_cases.delete_from_favorites import DeleteFromFavoritesUseCase
from src.core.user.use_cases.merge_favorites import MergeFavoritesUseCase
from src.core.user.use_cases.merge_comparison import MergeComparisonUseCase
from src.core.common.unit_of_work import UnitOfWork
from src.infrastructure.db.repositories.email_change_repo import SqlAlchemyEmailChangeRepository
from src.infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> UserRepository:
        return SqlAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_email_change_repo(self, session: AsyncSession) -> EmailChangeRepository:
        return SqlAlchemyEmailChangeRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_update_me_use_case(self, user_repo: UserRepository) -> UpdateMeUseCase:
        return UpdateMeUseCase(user_repo)

    @provide(scope=Scope.REQUEST)
    def provide_email_change_start_use_case(
        self,
        repo: EmailChangeRepository,
        user_repo: UserRepository,
        email_sender: EmailSender,
        sqlalchemy_uow: UnitOfWork,
        settings: Dynaconf,
    ) -> EmailChangeStartUseCase:
        return EmailChangeStartUseCase(
            repo=repo,
            user_repo=user_repo,
            email_sender=email_sender,
            frontend_base_url=str(settings.FRONTEND_BASE_URL),
            token_ttl_minutes=int(settings.AUTH_EMAIL_CHANGE_TOKEN_TTL_MINUTES),
            rate_limit_per_hour=int(settings.AUTH_EMAIL_CHANGE_RATE_LIMIT_PER_HOUR),
            uow=sqlalchemy_uow,
        )

    @provide(scope=Scope.REQUEST)
    def provide_email_change_confirm_use_case(
        self,
        repo: EmailChangeRepository,
        user_repo: UserRepository,
        sqlalchemy_uow: UnitOfWork
    ) -> EmailChangeConfirmUseCase:
        return EmailChangeConfirmUseCase(repo=repo, user_repo=user_repo, uow=sqlalchemy_uow)

    @provide(scope=Scope.REQUEST)
    def provide_add_to_comparison_use_case(self, user_repo: UserRepository, sqlalchemy_uow: UnitOfWork) -> AddToComparisonUseCase:
        return AddToComparisonUseCase(user_repo, sqlalchemy_uow)

    @provide(scope=Scope.REQUEST)
    def provide_remove_from_comparison_use_case(
        self, user_repo: UserRepository, slqalchemy_uow: UnitOfWork
    ) -> DeleteFromComparisonUseCase:
        return DeleteFromComparisonUseCase(user_repo, slqalchemy_uow)

    @provide(scope=Scope.REQUEST)
    def provide_add_to_favorites_use_case(self, user_repo: UserRepository, sqlalchemy_uow: UnitOfWork) -> AddToFavoritesUseCase:
        return AddToFavoritesUseCase(user_repo, sqlalchemy_uow)

    @provide(scope=Scope.REQUEST)
    def provide_remove_from_favorites_use_case(
        self, user_repo: UserRepository, sqlalchemy_uow: UnitOfWork
    ) -> DeleteFromFavoritesUseCase:
        return DeleteFromFavoritesUseCase(user_repo, sqlalchemy_uow)

    @provide(scope=Scope.REQUEST)
    def provide_merge_favorites_use_case(self, user_repo: UserRepository) -> MergeFavoritesUseCase:
        return MergeFavoritesUseCase(user_repo)

    @provide(scope=Scope.REQUEST)
    def provide_merge_comparisons_use_case(self, user_repo: UserRepository) -> MergeComparisonUseCase:
        return MergeComparisonUseCase(user_repo)
