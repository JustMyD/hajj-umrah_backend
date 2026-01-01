from typing import List

from src.core.tours.ports.tour_repository import TourRepository
from src.core.tours.read_models.get_tarifs_read_model import TourTarifReadModel


class GetTourTarifsUseCase:
    def __init__(self, repo: TourRepository):
        self.repo = repo

    async def execute(self) -> List[TourTarifReadModel]:
        items = await self.repo.get_tour_tarifs()
        return items
