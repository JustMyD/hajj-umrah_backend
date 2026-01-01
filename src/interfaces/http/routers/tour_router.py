from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from dishka.integrations.fastapi import FromDishka, inject

from src.interfaces.http.models.tour_model import (
    SearchToursRequest, ToursResponse, ToursAggregatesRequest, ToursAggregatesResponse, TourTarifsResponse,
    TourDepartureCitiesResponse, ToursIdsRequest
)
from src.core.tours.use_cases.search_tours import SearchToursUseCase
from src.core.tours.use_cases.get_tour_by_ids import GetTourByIdsUseCase
from src.core.tours.use_cases.get_tours_aggregates import GetToursAggregatesUseCase
from src.core.tours.use_cases.get_tarifs import GetTourTarifsUseCase
from src.core.tours.use_cases.get_tours_departure_cities import GetToursDepartureCitiesUseCase
from src.interfaces.http.mappers.tour_mapper import (
    map_search_tours_model_to_response, map_aggregates_tour_model_to_response, map_tour_tarif_model_to_response,
    map_tours_departure_cities_model_to_response
)

tour_router = APIRouter(prefix="/tours", tags=["tours"])


@tour_router.post("")
@inject
async def get_tours_by_filters(
    search_request: SearchToursRequest,
    search_tours_use_case: FromDishka[SearchToursUseCase],
    limit: Optional[int] = Query(default=20, ge=1),
    offset: Optional[int] = Query(default=0, ge=0),
) -> List[ToursResponse]:
    """
    Поиск туров по фильтрам
    """
    if search_request.departure_date_mode == "single" and search_request.departure_date is None:
        raise HTTPException(status_code=400, detail="Дата вылета обязательна для режима `single`")
    if search_request.departure_date_mode == "range" and (search_request.departure_date_start is None or search_request.departure_date_end is None):
        raise HTTPException(status_code=400, detail="Дата начала и окончания обязательны для режима `range`")
    params = search_request.model_dump()
    items = await search_tours_use_case.execute(**params, limit=limit, offset=offset)
    return [map_search_tours_model_to_response(item) for item in items]


@tour_router.post("/by_ids")
@inject
async def get_tours_by_ids(
    search_request: ToursIdsRequest,
    use_case: FromDishka[GetTourByIdsUseCase],
):
    """
    Поиск туров по ID
    """
    items = await use_case.execute(tour_ids=search_request.tour_ids)
    result = [map_search_tours_model_to_response(item) for item in items]
    return result


@tour_router.post("/aggregates")
@inject
async def get_tours_aggregates(
    search_request: ToursAggregatesRequest,
    get_tours_aggregates_use_case: FromDishka[GetToursAggregatesUseCase],
) -> List[ToursAggregatesResponse]:
    """
    Получение короткой сводки по ценам на туры
    """
    params = search_request.model_dump()
    items = await get_tours_aggregates_use_case.execute(**params)
    return [map_aggregates_tour_model_to_response(item) for item in items]


@tour_router.get("/tariffs")
@inject
async def get_tariffs(
    get_tours_tarifs_use_case: FromDishka[GetTourTarifsUseCase]
) -> List[TourTarifsResponse]:
    """
    Получение списка тарифов для туров
    """
    items = await get_tours_tarifs_use_case.execute()
    return [map_tour_tarif_model_to_response(item) for item in items]


@tour_router.get("/departure_cities")
@inject
async def get_departure_cities(
    get_tours_departure_cities_use_case: FromDishka[GetToursDepartureCitiesUseCase]
) -> List[TourDepartureCitiesResponse]:
    """
    Получение списка городов отправления
    """
    items = await get_tours_departure_cities_use_case.execute()
    return [map_tours_departure_cities_model_to_response(item) for item in items]
