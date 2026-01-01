from datetime import datetime
from typing import List, Optional, Literal

from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel
from src.core.tours.ports.tour_repository import TourRepository


class SearchToursUseCase:
    """
    UseCase для поиска туров
    """
    def __init__(self, repo: TourRepository):
        self.repo = repo

    async def execute(
        self,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
        departure_city: Optional[str],
        departure_date_mode: Literal["single", "range"],
        departure_date: Optional[datetime],
        departure_date_start: Optional[datetime],
        departure_date_end: Optional[datetime],
        pilgrims: Optional[int],
        limit: int = 20,
        offset: int = 0,
    ) -> List[TourSearchReadModel]:
        """
        Поиск туров
        """
        # application-level validation can be added here
        if limit <= 0 or offset < 0:
            raise ValueError("invalid pagination")
        return await self.repo.search(
            tour_type,
            tarif,
            operator_id,
            departure_city,
            departure_date_mode,
            departure_date,
            departure_date_start,
            departure_date_end,
            pilgrims,
            limit,
            offset,
        )
