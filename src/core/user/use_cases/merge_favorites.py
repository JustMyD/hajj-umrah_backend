from uuid import UUID
from typing import List

from src.core.user.ports.user_repository import UserRepository
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork


class MergeFavoritesUseCase(UseCase):
    def __init__(self, repo: UserRepository, uow: UnitOfWork):
        super().__init__(uow)
        self.repo = repo

    async def execute(self, tour_ids: List[UUID], user_id: UUID) -> None:
        try:
            await self.repo.merge_favorite_tours(tour_ids, user_id)
            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            raise e
