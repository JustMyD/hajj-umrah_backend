"""
ValueObject отеля
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class HotelInfo:
    """
        Информация об отеле
    """
    city: str
    name: str
    stars: Optional[int] = None  # 3..5
    rating: Optional[float] = None  # 0..5
    reviews_count: Optional[int] = None
    distance_text: Optional[str] = None
    maps_url: Optional[str] = None
    amenities: Optional[List[str]] = None

    def __post_init__(self):
        if self.stars is not None and not 0 <= self.stars <= 5:
            raise ValueError("stars must be between 0 and 5")
        if self.rating is not None and not 0.0 <= self.rating <= 5.0:
            raise ValueError("rating must be between 0 and 5")
