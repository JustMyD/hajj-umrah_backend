from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.operator.ports.operator_repository import OperatorRepository
from src.infrastructure.db.repositories.operator_repo import SqlAlchemyOperatorRepository
from src.core.operator.use_cases.search_operators import SearchOperatorsUseCase


class OperatorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_operator_repo(self, session: AsyncSession) -> OperatorRepository:
        return SqlAlchemyOperatorRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_search_operators_use_case(self, operator_repo: OperatorRepository) -> SearchOperatorsUseCase:
        return SearchOperatorsUseCase(operator_repo)