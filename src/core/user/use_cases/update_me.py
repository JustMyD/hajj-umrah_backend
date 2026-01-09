from __future__ import annotations

from dataclasses import replace
from datetime import date

from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.core.common.use_case import UseCase
from src.core.common.unit_of_work import UnitOfWork


class UpdateMeUseCase(UseCase):
    def __init__(self, user_repo: UserRepository, uow: UnitOfWork) -> None:
        super().__init__(uow)
        self.user_repo = user_repo

    async def execute(
        self,
        user: User,
        *,
        name: str | None = None,
        surname: str | None = None,
        phone: str | None = None,
        city: str | None = None,
        birth_date: date | None = None,
        email_notification: bool | None = None,
        sms_notification: bool | None = None,
    ) -> User:
        try:
            updated_model = replace(
                user,
                name=name if name is not None else user.name,
                surname=surname if surname is not None else user.surname,
                phone=phone if phone is not None else user.phone,
                city=city if city is not None else user.city,
                birth_date=birth_date if birth_date is not None else user.birth_date,
                email_notification=email_notification if email_notification is not None else user.email_notification,
                sms_notification=sms_notification if sms_notification is not None else user.sms_notification,
            )
            updated_user = await self.user_repo.update(updated_model)
            await self.uow.commit()
            return updated_user
        except Exception as e:
            await self.uow.rollback()
            raise e
