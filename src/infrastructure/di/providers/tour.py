from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tours.ports.tour_repository import TourRepository
from src.core.tours.use_cases.search_tours import SearchToursUseCase
from src.core.tours.use_cases.get_tour_by_ids import GetTourByIdsUseCase
from src.core.tours.use_cases.get_tarifs import GetTourTarifsUseCase
from src.core.tours.use_cases.get_tours_aggregates import GetToursAggregatesUseCase
from src.core.tours.use_cases.get_tours_departure_cities import GetToursDepartureCitiesUseCase
from src.infrastructure.db.repositories.tour_repo import SqlAlchemyTourRepository


class TourProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def provide_tour_repo(
        self,
        session: AsyncSession,
    ) -> TourRepository:
        return SqlAlchemyTourRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_search_tours_use_case(
        self,
        tour_repo: TourRepository,
    ) -> SearchToursUseCase:
        return SearchToursUseCase(tour_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_tours_by_ids(
            self,
            tour_repo: TourRepository,
    ) -> GetTourByIdsUseCase:
        return GetTourByIdsUseCase(tour_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_tours_aggregates_use_case(
        self,
        tour_repo: TourRepository,
    ) -> GetToursAggregatesUseCase:
        return GetToursAggregatesUseCase(tour_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_tours_tarifs_use_case(
        self,
        tour_repo: TourRepository,
    ) -> GetTourTarifsUseCase:
        return GetTourTarifsUseCase(tour_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_tours_departure_cities_use_case(
        self,
        tour_repo: TourRepository,
    ) -> GetToursDepartureCitiesUseCase:
        return GetToursDepartureCitiesUseCase(tour_repo)
