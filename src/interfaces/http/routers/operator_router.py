from typing import List

from fastapi import APIRouter, Query
from dishka.integrations.fastapi import FromDishka, inject

from src.core.operator.use_cases.search_operators import SearchOperatorsUseCase
from src.interfaces.http.models.operator_model import OperatorsResponse
from src.interfaces.http.mappers.operator_mapper import map_operator_model_to_response

operators_router = APIRouter(prefix="/operators", tags=["operator"])


@operators_router.get("")
@inject
async def get_operators(
    search_operators_use_case: FromDishka[SearchOperatorsUseCase],
    limit: int = Query(default=20, gt=0),
    offset: int = Query(default=0, ge=0),
) -> List[OperatorsResponse]:
    """
    Получить список с данными туроператоров
    """
    items = await search_operators_use_case.execute(limit=limit, offset=offset)
    return [map_operator_model_to_response(item) for item in items]
