from typing import List, Optional

from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel
from src.core.tours.read_models.tours_aggregates_read_model import ToursAggregatesReadModel
from src.core.tours.read_models.get_tarifs_read_model import TourTarifReadModel
from src.core.tours.read_models.tours_departure_cities_read_model import ToursDepartureCitiesReadModel
from src.interfaces.http.models.tour_model import (
    ToursResponse,
    TourOperator,
    FlightNode,
    FlightDirection,
    TourFlights,
    TourHotels,
    ToursAggregatesResponse,
    TourTarifsResponse,
    TourDepartureCitiesResponse,
)


def map_search_tours_model_to_response(item: TourSearchReadModel) -> ToursResponse:
    operator = TourOperator(
        name=item.operator_name,
        logo=item.operator_logo,
        foundation_year=item.operator_foundation_year,
        verified=item.operator_verified,
        features=item.operator_features,
    )

    outbound = _find_direction(item.flights, "outbound")
    inbound = _find_direction(item.flights, "inbound")

    flights = TourFlights(
        outbound=_map_direction(outbound) if outbound else _empty_direction(),
        inbound=_map_direction(inbound) if inbound else _empty_direction(),
    )

    hotels = [
        TourHotels(
            city=h.get("city", ""),
            name=h.get("name", ""),
            stars=h.get("stars"),
            rating=h.get("rating"),
            reviewsCount=h.get("reviews_count"),
            distanceText=h.get("distance_text"),
            externalLink=h.get("maps_url"),
            amenities=h.get("amenities", []),
        )
        for h in item.hotels
    ]

    return ToursResponse(
        id=item.id,
        operator=operator,
        title=item.title,
        type=item.type,
        price=item.price,
        originalPrice=item.original_price,
        duration=item.duration,
        location=item.location,
        visaIncluded=item.visa_included,
        availability=item.availability,
        tarif=item.tarif,
        flights=flights,
        hotels=hotels,
    )


def _find_direction(flights: List[dict], direction: str) -> Optional[dict]:
    for f in flights:
        if f.get("direction") == direction:
            return f
    return None


def _map_direction(direction: dict) -> FlightDirection:
    nodes_raw = direction.get("nodes", []) or []
    nodes = []

    for idx, node in enumerate(nodes_raw):
        node_type = "endpoint" if idx == 0 or idx == len(nodes_raw) - 1 else "layover"
        nodes.append(
            FlightNode(
                type=node_type,
                iata=node.get("iata", ""),
                city=node.get("city", ""),
                layoverMinutes=node.get("layover_minutes"),
            )
        )

    from_city = nodes_raw[0].get("city", "") if nodes_raw else ""
    from_iata = nodes_raw[0].get("iata", "") if nodes_raw else ""
    to_city = nodes_raw[-1].get("city", "") if nodes_raw else ""
    to_iata = nodes_raw[-1].get("iata", "") if nodes_raw else ""

    departure_date = direction.get("departure_date")
    if departure_date and hasattr(departure_date, "isoformat"):
        departure_date = departure_date.isoformat()

    return FlightDirection(
        fromCity=from_city,
        fromIata=from_iata,
        toCity=to_city,
        toIata=to_iata,
        departureDate=departure_date or "",
        nodes=nodes,
        included=direction.get("inclusions", []),
    )


def _empty_direction() -> FlightDirection:
    return FlightDirection(
        fromCity="",
        fromIata="",
        toCity="",
        toIata="",
        departureDate="",
        nodes=[],
        included=[],
    )


def map_aggregates_tour_model_to_response(item: ToursAggregatesReadModel) -> ToursAggregatesResponse:
    return ToursAggregatesResponse(
        date=item.date,
        avg_price=item.avg_price,
        min_price=item.min_price,
        tours_count=item.tours_count,
    )


def map_tour_tarif_model_to_response(item: TourTarifReadModel) -> TourTarifsResponse:
    return TourTarifsResponse(id=item.id, label=item.label)


def map_tours_departure_cities_model_to_response(item: ToursDepartureCitiesReadModel) -> TourDepartureCitiesResponse:
    return TourDepartureCitiesResponse(id=item.id, label=item.label)
