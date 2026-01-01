from __future__ import annotations

from datetime import datetime, timezone
from typing import List
import logging
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.infrastructure.db.models.users import Users, UserComparisons, UserFavorites


def _to_entity(model: Users) -> User:
    return User(
        id=model.id,
        email=model.email,
        email_verified_at=model.email_verified_at,
        name=model.name,
        surname=model.surname,
        phone=model.phone,
        city=model.city,
        birth_date=model.birth_date,
        email_notification=model.email_notification,
        sms_notification=model.sms_notification,
        favorite_tour_ids=[fav.tour_id for fav in model.favorites],
        comparison_tour_ids=[comp.tour_id for comp in model.comparisons],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        res = await self.session.execute(
            select(Users)
            .where(Users.id == user_id)
            .options(selectinload(Users.favorites), selectinload(Users.comparisons))
        )
        model = res.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(
            select(Users)
            .where(Users.email == email)
            .options(selectinload(Users.favorites), selectinload(Users.comparisons))
        )
        model = res.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = Users(
            id=user.id,
            email=user.email,
            email_verified_at=user.email_verified_at,
            name=user.name,
            surname=user.surname,
            phone=user.phone,
            city=user.city,
            birth_date=user.birth_date,
            email_notification=user.email_notification,
            sms_notification=user.sms_notification,
            created_at=user.created_at or datetime.now(timezone.utc),
            updated_at=user.updated_at or datetime.now(timezone.utc),
        )
        self.session.add(model)
        await self.session.flush()
        # Перезагружаем модель с загруженными связанными данными (favorites/comparisons)
        refreshed = await self.get_by_id(user.id)
        if refreshed is None:
            raise RuntimeError("user not found after create")
        return refreshed

    async def update(self, user: User) -> User:
        await self.session.execute(
            update(Users)
            .where(Users.id == user.id)
            .values(
                email=user.email,
                email_verified_at=user.email_verified_at,
                name=user.name,
                surname=user.surname,
                phone=user.phone,
                city=user.city,
                birth_date=user.birth_date,
                email_notification=user.email_notification,
                sms_notification=user.sms_notification,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        refreshed = await self.get_by_id(user.id)
        if refreshed is None:
            raise RuntimeError("user not found for update")
        return refreshed

    async def delete(self, user_id: UUID) -> None:
        await self.session.execute(delete(Users).where(Users.id == user_id))

    async def add_favorite_tour(self, user_id: UUID, tour_id: UUID) -> bool:
        stmt = insert(UserFavorites).values(
            user_id=user_id,
            tour_id=tour_id,
        ).on_conflict_do_nothing()

        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

    async def remove_favorite_tour(self, user_id: UUID, tour_id: UUID) -> bool:
        stmt = delete(UserFavorites).where(UserFavorites.user_id == user_id, UserFavorites.tour_id == tour_id)
        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

    async def add_comparison_tour(self, user_id: UUID, tour_id: UUID) -> bool:
        stmt = insert(UserComparisons).values(
            user_id=user_id,
            tour_id=tour_id,
        ).on_conflict_do_nothing()

        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

    async def remove_comparison_tour(self, user_id: UUID, tour_id: UUID) -> bool:
        stmt = delete(UserComparisons).where(UserComparisons.user_id == user_id, UserComparisons.tour_id == tour_id)
        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

    async def merge_favorite_tours(self, tour_ids: List[UUID], user_id: UUID) -> bool:
        """
        Слияние локального и онлайн списков избранного
        """
        if not tour_ids:
            return True

        stmt = insert(UserFavorites).values([
            {
                "user_id": user_id,
                "tour_id": tour_id,
            }
            for tour_id in tour_ids
        ]).on_conflict_do_nothing(
            index_elements=["user_id", "tour_id"]
        )

        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False

    async def merge_comparison_tours(self, tour_ids: List[UUID], user_id: UUID) -> bool:
        """
        Слияние локального и онлайн списков сравнения
        """
        if not tour_ids:
            return True

        stmt = insert(UserComparisons).values([
            {
                "user_id": user_id,
                "tour_id": tour_id,
            }
            for tour_id in tour_ids
        ]).on_conflict_do_nothing(
            index_elements=["user_id", "tour_id"]
        )

        try:
            await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(str(e))
            return False
