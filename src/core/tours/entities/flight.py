from typing import List, Optional, Literal, Type
from datetime import datetime
from dataclasses import dataclass

IATACode = Type[str]
NodeType = Literal["endpoint", "layover"]


@dataclass(frozen=True)
class FlightNode:
    type: NodeType
    iata: IATACode
    city: str
    layover_minutes: Optional[int] = None

    def __post_init__(self):
        if self.type not in ("endpoint", "layover"):
            raise ValueError("Тип точки перелета `FlightNode.type` должен быть 'endpoint' или 'layover'")
        if self.type == "layover" and (self.layover_minutes is None or self.layover_minutes < 0):
            raise ValueError("Время пересадки должно быть >= 0")


@dataclass(frozen=True)
class FlightDirection:
    from_city: str
    from_iata: IATACode
    to_city: str
    to_iata: IATACode
    departure_date: datetime
    nodes: List[FlightNode]
    included: List[str]

    def __post_init__(self):
        if not self.nodes:
            raise ValueError("Точки перелета должны быть заполнены")
        if self.nodes[0].iata != self.from_iata or self.nodes[-1].iata != self.to_iata:
            raise ValueError("Не совпадает код аэропорта в точке взлета/посадки параметра nodes и from_iata/to_iata")
        if self.nodes[0].city != self.from_city or self.nodes[-1].city != self.to_city:
            raise ValueError("Не совпадает название города в точке взлета/посадки параметра nodes и from_city/to_city")


@dataclass(frozen=True)
class TourFlights:
    outbound: FlightDirection
    inbound: FlightDirection
