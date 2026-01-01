from dataclasses import dataclass


@dataclass(frozen=True)
class TourTarifReadModel:
    id: int
    label: str
