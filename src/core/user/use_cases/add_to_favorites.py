from uuid import UUID

from src.core.user.ports.user_repository import UserRepository
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork


class AddToFavoritesUseCase(UseCase):
    def __init__(self, repo: UserRepository, uow: UnitOfWork):
        super().__init__(uow)
        self.repo = repo

    async def execute(self, user_id: UUID, tour_id: UUID) -> None:
        try:
            await self.repo.add_favorite_tour(user_id, tour_id)
            await self.uow.commit()
        except Exception as e:
            await self.uow.rollback()
            raise e
