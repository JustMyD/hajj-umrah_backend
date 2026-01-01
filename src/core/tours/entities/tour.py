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
#
# class TourType(str, Enum):
#     umrah = "umrah"
#     hajj = "hajj"
#     all = "all"
#
#
# class Tour_Tarifs(str, Enum):
#     budget = "budget"
#     standard = "standard"
#     comfort = "comfort"
#     premium = "premium"


@dataclass(frozen=True)
class Tour:
    id: UUID
    operator: TourOperator
    title: Optional[str]
    type: str  # Значение из таблицы tour_types
    price: Price
    original_price: Price | None
    duration: int
    location: List[str]
    visa_included: bool
    availability: str  # Значение из таблицы availability
    # availability_max_count: int
    # availability_current_count: int
    tarif: str  # Значение из таблицы tour_tarifs
    flights: TourFlights
    hotels: List[HotelInfo]
    is_published: bool = False

    def is_available(self) -> bool:
        """
        Доступность
        """
        return self.availability != 'sold_out'
