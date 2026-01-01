from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class ToursAggregatesReadModel:
    date: datetime
    avg_price: int
    min_price: int
    tours_count: int
