from __future__ import annotations

import secrets
from uuid import UUID
from typing import List

from dynaconf import Dynaconf
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from dishka.integrations.fastapi import FromDishka, inject

from src.core.user.entities.user import User
from src.core.tours.use_cases.get_tour_by_ids import GetTourByIdsUseCase
from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel
from src.core.user.use_cases.email_change_confirm import EmailChangeConfirmUseCase
from src.core.user.use_cases.email_change_start import EmailChangeStartUseCase
from src.core.user.use_cases.update_me import UpdateMeUseCase
from src.core.user.use_cases.add_to_comparison import AddToComparisonUseCase
from src.core.user.use_cases.delete_from_comparison import DeleteFromComparisonUseCase
from src.core.user.use_cases.add_to_favorites import AddToFavoritesUseCase
from src.core.user.use_cases.delete_from_favorites import DeleteFromFavoritesUseCase
from src.core.user.use_cases.merge_comparison import MergeComparisonUseCase
from src.core.user.use_cases.merge_favorites import MergeFavoritesUseCase
from src.core.user.use_cases.email_change_start import RateLimitError
from src.infrastructure.auth.magic_tokens import hash_token
from src.interfaces.http.dependencies.current_user import get_current_user
from src.interfaces.http.mappers.user_mapper import map_user_to_response
from src.interfaces.http.mappers.tour_mapper import map_search_tours_model_to_response
from src.interfaces.http.models.user_model import (
    UpdateMeRequest,
    UserResponse,
    EmailChangeStartRequest,
    EmailChangeConfirmRequest,
    OkResponse,
    AddToUserListRequest,
    RemoveFromUserListRequest,
    MergeUserListRequest,
)
from src.interfaces.http.models.tour_model import ToursResponse


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.patch("/me", response_model=UserResponse)
@inject
async def update_me(
    body: UpdateMeRequest,
    use_case: FromDishka[UpdateMeUseCase],
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    updated = await use_case.execute(
        current_user,
        name=body.name,
        surname=body.surname,
        phone=body.phone,
        city=body.city,
        birth_date=body.birth_date,
        email_notification=body.email_notification,
        sms_notification=body.sms_notification,
    )
    return map_user_to_response(updated)


@user_router.post("/me/email/change/start", response_model=OkResponse)
@inject
async def email_change_start(
    body: EmailChangeStartRequest,
    use_case: FromDishka[EmailChangeStartUseCase],
    settings: FromDishka[Dynaconf],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(token=raw_token, pepper=str(settings.AUTH_EMAIL_CHANGE_TOKEN_PEPPER))
    try:
        await use_case.execute(
            user=current_user,
            new_email=body.new_email,
            raw_token=raw_token,
            token_hash=token_hash,
        )
        return OkResponse(ok=True)
    except RateLimitError:
        # Маскируем ошибку от злоумышленника
        return OkResponse(ok=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/me/email/change/confirm", response_model=UserResponse)
@inject
async def email_change_confirm(
    body: EmailChangeConfirmRequest,
    request: Request,
    use_case: FromDishka[EmailChangeConfirmUseCase],
    settings: FromDishka[Dynaconf],
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    token_hash = hash_token(token=body.token, pepper=str(settings.AUTH_EMAIL_CHANGE_TOKEN_PEPPER))
    result = await use_case.execute(
        user=current_user,
        token_hash=token_hash,
        request_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    return map_user_to_response(result.user)


@user_router.put("/me/favorites", response_model=OkResponse)
@inject
async def add_tour_to_favorites(
    body: AddToUserListRequest,
    use_case: FromDishka[AddToFavoritesUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    await use_case.execute(user_id=current_user.id, tour_id=body.tour_id)
    return OkResponse(ok=True)


@user_router.delete("/me/favorites", response_model=OkResponse)
@inject
async def delete_tour_from_favorites(
    body: RemoveFromUserListRequest,
    use_case: FromDishka[DeleteFromFavoritesUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    await use_case.execute(user_id=current_user.id, tour_id=body.tour_id)
    return OkResponse(ok=True)


@user_router.post("/me/favorites/merge", response_model=OkResponse)
@inject
async def merge_tour_from_favorites(
    body: MergeUserListRequest,
    use_case: FromDishka[MergeFavoritesUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    result = await use_case.execute(tour_ids=body.tour_ids, user_id=current_user.id)
    return OkResponse(ok=result)


@user_router.put("/me/comparison", response_model=OkResponse)
@inject
async def add_tour_to_comparison(
    body: AddToUserListRequest,
    use_case: FromDishka[AddToComparisonUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    await use_case.execute(user_id=current_user.id, tour_id=body.tour_id)
    return OkResponse(ok=True)


@user_router.delete("/me/comparison", response_model=OkResponse)
@inject
async def delete_tour_from_comparison(
    body: RemoveFromUserListRequest,
    use_case: FromDishka[DeleteFromComparisonUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    await use_case.execute(user_id=current_user.id, tour_id=body.tour_id)
    return OkResponse(ok=True)


@user_router.post("/me/comparison/merge", response_model=OkResponse)
@inject
async def merge_tour_from_comparison(
    body: MergeUserListRequest,
    use_case: FromDishka[MergeComparisonUseCase],
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    await use_case.execute(tour_ids=body.tour_ids, user_id=current_user.id)
    return OkResponse(ok=True)


@user_router.get("/me/favorites", response_model=List[ToursResponse])
@inject
async def get_user_favorites(
    get_tours_by_ids_uc: FromDishka[GetTourByIdsUseCase],
    current_user: User = Depends(get_current_user),
) -> List[ToursResponse]:
    tour_ids: List[UUID] = current_user.favorite_tour_ids
    tours: List[TourSearchReadModel] = await get_tours_by_ids_uc.execute(tour_ids=tour_ids)
    return [map_search_tours_model_to_response(item) for item in tours]


@user_router.get("/me/comparison", response_model=List[ToursResponse])
@inject
async def get_user_comparison(
    get_tours_by_ids_uc: FromDishka[GetTourByIdsUseCase],
    current_user: User = Depends(get_current_user),
) -> List[ToursResponse]:
    tour_ids: List[UUID] = current_user.comparison_tour_ids
    tours: List[TourSearchReadModel] = await get_tours_by_ids_uc.execute(tour_ids=tour_ids)
    return [map_search_tours_model_to_response(item) for item in tours]
