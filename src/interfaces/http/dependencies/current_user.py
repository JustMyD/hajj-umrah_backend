from __future__ import annotations

from fastapi import Header, HTTPException
from dishka.integrations.fastapi import FromDishka, inject

from src.core.auth.ports.token_service import TokenService
from src.core.user.entities.user import User
from src.core.user.ports.user_repository import UserRepository
from src.infrastructure.auth.jwt_token_service import TokenError


@inject
async def get_current_user(
    token_service: FromDishka[TokenService],
    user_repo: FromDishka[UserRepository],
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        user_id = token_service.verify_access_token(token)
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


