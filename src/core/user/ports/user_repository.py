from abc import ABC, abstractmethod
from uuid import UUID
from typing import List

from src.core.user.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_favorite_tour(self, user_id: UUID, tour_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_favorite_tour(self, user_id: UUID, tour_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_comparison_tour(self, user_id: UUID, tour_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_comparison_tour(self, user_id: UUID, tour_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def merge_favorite_tours(self, tour_ids: List[UUID], user_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def merge_comparison_tours(self, tour_ids: List[UUID], user_id: UUID) -> None:
        raise NotImplementedError
