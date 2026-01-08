from uuid import UUID
from typing import List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class TourSearchReadModel:
    id: UUID

    operator_name: str
    operator_logo: str
    operator_foundation_year: int
    operator_verified: bool
    operator_features: List[str]

    title: str
    type: dict
    tarif: dict
    price: int
    original_price: Optional[int]
    duration: int
    location: str
    visa_included: bool
    availability: str

    flights: List[dict]
    hotels: List[dict]
