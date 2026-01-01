from typing import List

from src.core.tours.ports.tour_repository import TourRepository
from src.core.tours.read_models.tours_departure_cities_read_model import ToursDepartureCitiesReadModel


class GetToursDepartureCitiesUseCase:
    def __init__(self, repo: TourRepository):
        self.repo = repo

    async def execute(self) -> List[ToursDepartureCitiesReadModel]:
        return await self.repo.get_tours_departure_cities()
