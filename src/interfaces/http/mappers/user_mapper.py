from __future__ import annotations

from src.core.user.entities.user import User
from src.interfaces.http.models.user_model import UserResponse


def map_user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        surname=user.surname,
        phone=user.phone,
        city=user.city,
        birth_date=user.birth_date,
        email_notification=user.email_notification,
        sms_notification=user.sms_notification,
        favorite_tour_ids=user.favorite_tour_ids,
        comparison_tour_ids=user.comparison_tour_ids,
    )


