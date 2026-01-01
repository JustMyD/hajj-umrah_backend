from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TourOperator:
    name: str
    logo: str
    foundation_year: int
    verified: bool
    features: List[str]

    # def __post_init__(self):
    #     if self.years_on_market < 0:
    #         raise ValueError("years_on_market must be >= 0")