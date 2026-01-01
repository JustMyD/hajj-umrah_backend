from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, NaiveDatetime


class SearchToursRequest(BaseModel):
    tour_type: Optional[str] = Field(default=None, description="Тип тура")
    tarif: Optional[str] = Field(default=None, description="Тариф")
    operator_id: Optional[int] = Field(default=None, description="ID туроператора")
    departure_city: Optional[str] = Field(default=None, description="Город вылета")
    departure_date_mode: str = Field(description="Режим выбора даты вылета [`single`, `range`]")
    departure_date: Optional[NaiveDatetime] = Field(default=None, description="Дата вылета для режима `single`")
    departure_date_start: Optional[NaiveDatetime] = Field(default=None, description="Дата начала для режима `range`")
    departure_date_end: Optional[NaiveDatetime] = Field(default=None, description="Дата окончания для режима `range`")
    pilgrims: Optional[int] = Field(default=1, description="Количество паломников")


class ToursAggregatesRequest(BaseModel):
    from_date: NaiveDatetime = Field(description="Начало диапазона")
    to_date: NaiveDatetime = Field(description="Конец диапазона")
    tour_type: Optional[str] = Field(default=None, description="Тип тура")
    tarif: Optional[str] = Field(default=None, description="Тариф")
    operator_id: Optional[int] = Field(default=None, description="ID туроператора")
    pilgrims: Optional[int] = Field(default=1, description="Количество паломников")


class TourOperator(BaseModel):
    name: str = Field(description="Название туроператора")
    logo: str = Field(description="Путь до изображения")
    yearsOnMarket: int = Field(description="Сколько лет на рынке")
    verified: bool = Field(description="Аккредитация Хадж миссия РФ")
    features: List[str] = Field(description="Особенности туроператора")


class FlightNode(BaseModel):
    type: Literal["endpoint", "layover"] = Field(description="Тип точки перелета. endpoint - взлет/посадка, layover - пересадка")
    iata: str = Field(description="Код IATA аэропорта")
    city: str = Field(description="Название города")
    layoverMinutes: Optional[int] = Field(default=None, description="Время ожидания при пересадке")


class FlightDirection(BaseModel):
    fromCity: str = Field(description="Название города взлета")
    fromIata: str = Field(description="Код IATA аэропорта взлета")
    toCity: str = Field(description="Название города приземления")
    toIata: str = Field(description="Код IATA аэропорта приземления")
    departureDate: str = Field(description="Дата вылета")
    nodes: List[FlightNode] = Field(description="Список города перелета, в случае пересадок")
    included: List[str] = Field(description="Что включено в перелет")


class TourFlights(BaseModel):
    outbound: FlightDirection = Field(description="Описание перелета туда")
    inbound: FlightDirection = Field(description="Описание перелета обратно")


class TourHotels(BaseModel):
    city: str = Field(description="Город отеля")
    name: str = Field(description="Название отеля")
    stars: Optional[int] = Field(default=None, description="Уровень отеля (звезды)")
    rating: Optional[float] = Field(default=None, description="Рейтинг отеля (оценка по отзывам)")
    reviewsCount: Optional[int] = Field(default=None, description="Количество отзывов")
    distanceText: Optional[str] = Field(default=None, description="Дополнительный текст (как далеко от мечети)")
    externalLink: Optional[str] = Field(default=None, description="Внешняя ссылка на отель (карты)")
    amenities: List[str] = Field(default_factory=list, description="Что включено из удобств")


class ToursResponse(BaseModel):
    id: UUID
    operator: TourOperator
    title: Optional[str] = Field(description="Название тура")
    type: str = Field(description="Тип умра/хадж")
    price: int = Field(description="Цена конкретного вылета")
    originalPrice: Optional[int] = Field(description="Изначальная цена тура")
    duration: int = Field(description="Продолжительность тура")
    location: str = Field(description="Посещаемые города")
    visaIncluded: bool
    availability: str = Field(description="Статус доступности")
    tarif: str = Field(description="Тариф")
    flights: TourFlights
    hotels: List[TourHotels]


class ToursAggregatesResponse(BaseModel):
    date: datetime
    avg_price: int
    min_price: int
    tours_count: int


class TourTarifsResponse(BaseModel):
    id: int
    label: str


class TourDepartureCitiesResponse(BaseModel):
    id: int
    label: str


class ToursIdsRequest(BaseModel):
    tour_ids: List[UUID]
