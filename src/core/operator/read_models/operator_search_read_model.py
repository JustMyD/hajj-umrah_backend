from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorSearchReadModel:
    id: int
    name: str
    description: str
    logo: str
    foundation_year: int
    rating: float
    reviews_count: int
    specialisations: List[str]
    features: List[str]
    certificates: List[str]
    verified: bool
