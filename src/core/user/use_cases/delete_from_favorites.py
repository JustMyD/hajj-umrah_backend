from uuid import UUID

from src.core.user.ports.user_repository import UserRepository


class DeleteFromFavoritesUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, user_id: UUID, tour_id: UUID) -> bool:
        try:
            result = await self.repo.remove_favorite_tour(user_id, tour_id)
            await self.repo.session.commit()
        except Exception as e:
            await self.repo.session.rollback()
            result = False

        return result
