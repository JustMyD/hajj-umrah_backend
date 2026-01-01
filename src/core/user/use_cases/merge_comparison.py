from uuid import UUID
from typing import List

from src.core.user.ports.user_repository import UserRepository


class MergeComparisonUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, tour_ids: List[UUID], user_id: UUID) -> bool:
        return await self.repo.merge_comparison_tours(tour_ids, user_id)
