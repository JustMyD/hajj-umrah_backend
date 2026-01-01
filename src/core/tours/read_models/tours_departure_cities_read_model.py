from dataclasses import dataclass


@dataclass(frozen=True)
class ToursDepartureCitiesReadModel:
    id: int
    label: str
