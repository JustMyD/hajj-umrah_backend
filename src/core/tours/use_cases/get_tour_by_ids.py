from uuid import UUID
from typing import List

from src.core.tours.ports.tour_repository import TourRepository
from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel


class ToursNotFoundError(Exception):
    pass


class GetTourByIdsUseCase:
    """
    UseCase для получения списка туров по списку ID
    """
    def __init__(self, repo: TourRepository):
        self.repo = repo

    async def execute(self, tour_ids: List[UUID]) -> List[TourSearchReadModel]:
        tours = await self.repo.get_by_id(tour_ids)
        return tours