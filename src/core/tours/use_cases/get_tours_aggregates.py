from typing import Optional, List
from datetime import datetime

from src.core.tours.read_models.tours_aggregates_read_model import ToursAggregatesReadModel
from src.core.tours.ports.tour_repository import TourRepository


class GetToursAggregatesUseCase:
    def __init__(self, tour_repo: TourRepository):
        self.repo = tour_repo

    async def execute(
        self,
        from_date: datetime,
        to_date: datetime,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
        pilgrims: Optional[int]
    ) -> List[ToursAggregatesReadModel]:
        aggregates_read_models: List[ToursAggregatesReadModel] = await self.repo.get_tours_aggregates(
            from_date, to_date, tour_type, tarif, operator_id
        )
        # Business rules
        result = aggregates_read_models

        return result
