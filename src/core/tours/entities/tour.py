from uuid import UUID
from dataclasses import dataclass
from typing import List, Optional

from src.core.tours.entities.price import Price
from src.core.tours.entities.operator import TourOperator
from src.core.tours.entities.hotel import HotelInfo
from src.core.tours.entities.flight import TourFlights

# Availability = Literal["available", "limited", "sold_out"]
# TourType = Literal["umrah", "hajj"]
# TourTarifs = Literal["budget", "standard", "comfort", "premium"]


# class Availability(str, Enum):
#     available = "available"
#     limited = "limited"
#     sold_out = "sold_out"
#

@dataclass(frozen=True)
class TourType:
    value: str
    label: str


@dataclass(frozen=True)
class TourTarifs:
    value: str
    label: str


@dataclass(frozen=True)
class Tour:
    id: UUID
    operator: TourOperator
    title: Optional[str]
    type: TourType
    price: Price
    original_price: Price | None
    duration: int
    location: List[str]
    visa_included: bool
    availability: str  # Значение из таблицы availability
    # availability_max_count: int
    # availability_current_count: int
    tarif: TourTarifs
    flights: TourFlights
    hotels: List[HotelInfo]
    is_published: bool = False

    def is_available(self) -> bool:
        """
        Доступность
        """
        return self.availability != 'sold_out'
