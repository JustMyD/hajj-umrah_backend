from typing import List

from pydantic import BaseModel


class OperatorsResponse(BaseModel):
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
