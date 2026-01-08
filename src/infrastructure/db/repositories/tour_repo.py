from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional, Literal, List

from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tours.read_models.get_tarifs_read_model import TourTarifReadModel
from src.core.tours.read_models.tours_aggregates_read_model import ToursAggregatesReadModel
from src.core.tours.ports.tour_repository import TourRepository
from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel
from src.core.tours.read_models.tours_departure_cities_read_model import ToursDepartureCitiesReadModel
from src.infrastructure.db.models.flights import Flights, FlightDirection, FlightDirectionNodes
from src.infrastructure.db.models.tours import Tours
from src.infrastructure.db.models.enums import TourType, TourTarif, Availability, DepartureCities


class SqlAlchemyTourRepository(TourRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tour_ids: List[UUID]) -> List[TourSearchReadModel]:
        if not tour_ids:
            return []

        # tour_id - это UUID для таблицы Flights, а не Tours
        stmt = (
            select(Flights)
            .join(Flights.tour)
            .where(Flights.id.in_(tour_ids))
            .options(
                selectinload(Flights.tour).selectinload(Tours.type),
                selectinload(Flights.tour).selectinload(Tours.tarif),
                selectinload(Flights.tour).selectinload(Tours.price_currency),
                selectinload(Flights.tour).selectinload(Tours.hotels),
                selectinload(Flights.availability_status),
                selectinload(Flights.directions).selectinload(FlightDirection.flight_nodes),
            )
        )
        result = await self.session.execute(stmt)
        flights = result.scalars().unique().all()

        # Используем ту же логику, что и в search для создания read model
        return [
            TourSearchReadModel(
                id=flight.id,
                operator_name=flight.tour.operator_name,
                operator_logo=flight.tour.operator_logo,
                operator_foundation_year=flight.tour.operator_foundation_year,
                operator_verified=flight.tour.operator_verified,
                operator_features=flight.tour.operator_features,
                title=flight.tour.title,
                type={"value": flight.tour.type.value, "label": flight.tour.type.label},
                tarif={"value": flight.tour.tarif.value, "label": flight.tour.tarif.label},
                price=int(flight.price),
                original_price=None,
                duration=flight.tour.duration,
                location=flight.tour.location,
                visa_included=flight.tour.visa_included,
                availability=flight.availability_status.value,  # Получаем значение через relationship
                flights=[
                    {
                        "id": direction.id,
                        "direction": direction.direction,
                        "departure_date": direction.departure_date,
                        "inclusions": direction.inclusions,
                        "nodes": [
                            {
                                "id": node.id,
                                "iata": node.iata,
                                "city": node.city,
                                "layover_minutes": node.layover_minutes,
                            }
                            for node in direction.flight_nodes
                        ],
                    }
                    for direction in flight.directions
                ],
                hotels=[
                    {
                        "id": hotel.id,
                        "city": hotel.city,
                        "name": hotel.name,
                        "stars": hotel.stars,
                        "rating": hotel.rating,
                        "reviews_count": hotel.reviews_count,
                        "distance_text": hotel.distance_text,
                        "maps_url": hotel.maps_url,
                        "amenities": hotel.amenities,
                    }
                    for hotel in flight.tour.hotels
                ],
            ) for flight in flights
        ]

    async def search(
        self,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
        departure_city: Optional[str],
        departure_date_mode: Literal["single", "range"],
        departure_date: Optional[datetime],
        departure_date_start: Optional[datetime],
        departure_date_end: Optional[datetime],
        pilgrims: Optional[int],
        limit: int = 20,
        offset: int = 0,
    ) -> List[TourSearchReadModel]:
        stmt = select(Flights).join(Flights.tour)

        if tour_type:
            # JOIN с таблицей tour_types для сравнения по value
            tour_type_alias = aliased(TourType)
            stmt = stmt.join(tour_type_alias, Tours.type_id == tour_type_alias.id)
            stmt = stmt.where(tour_type_alias.value == tour_type)

        if tarif:
            # JOIN с таблицей tour_tarifs для сравнения по value
            tarif_alias = aliased(TourTarif)
            stmt = stmt.join(tarif_alias, Tours.tarif_id == tarif_alias.id)
            stmt = stmt.where(tarif_alias.value == tarif)

        if operator_id:
            stmt = stmt.where(Tours.operator_id == operator_id)

        # JOIN с таблицей availability для фильтрации по sold_out
        availability_alias = aliased(Availability)
        stmt = stmt.join(availability_alias, Flights.availability_status_id == availability_alias.id)
        stmt = stmt.where(availability_alias.value != 'sold_out')

        outbound_direction = aliased(FlightDirection)
        outbound_nodes = aliased(FlightDirectionNodes)
        need_outbound_join = departure_city or departure_date or departure_date_start or departure_date_end

        if need_outbound_join:
            stmt = stmt.join(
                outbound_direction,
                and_(
                    outbound_direction.flight_id == Flights.id,
                    outbound_direction.direction == "outbound",
                ),
            )

        if departure_city:
            stmt = stmt.join(
                outbound_nodes,
                outbound_nodes.flight_direction_id == outbound_direction.id,
            ).where(outbound_nodes.city == departure_city)

        if departure_date_mode == "single" and departure_date:
            # Сравниваем по дню, а не по точному времени
            # Создаем начало и конец дня для корректного сравнения
            start_of_day = departure_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            stmt = stmt.where(
                outbound_direction.departure_date >= start_of_day,
                outbound_direction.departure_date < end_of_day
            )

        if departure_date_mode == "range" and departure_date_start and departure_date_end:
            stmt = stmt.where(
                outbound_direction.departure_date.between(departure_date_start, departure_date_end)
            )

        stmt = stmt.distinct(Flights.id).limit(limit).offset(offset).options(
            selectinload(Flights.tour).selectinload(Tours.hotels),
            selectinload(Flights.tour).selectinload(Tours.type),
            selectinload(Flights.tour).selectinload(Tours.tarif),
            selectinload(Flights.tour).selectinload(Tours.price_currency),
            selectinload(Flights.availability_status),
            selectinload(Flights.directions).selectinload(FlightDirection.flight_nodes),
        )

        result = await self.session.execute(stmt)
        models = result.scalars().unique().all()

        return [
            TourSearchReadModel(
                id=flight.id,
                operator_name=flight.tour.operator_name,
                operator_logo=flight.tour.operator_logo,
                operator_foundation_year=flight.tour.operator_foundation_year,
                operator_verified=flight.tour.operator_verified,
                operator_features=flight.tour.operator_features,
                title=flight.tour.title,
                type={"value": flight.tour.type.value, "label": flight.tour.type.label},
                tarif={"value": flight.tour.tarif.value, "label": flight.tour.tarif.label},
                price=int(flight.price),
                original_price=None,
                duration=flight.tour.duration,
                location=flight.tour.location,
                visa_included=flight.tour.visa_included,
                availability=flight.availability_status.value,  # Получаем значение через relationship
                flights=[
                    {
                        "id": direction.id,
                        "direction": direction.direction,
                        "departure_date": direction.departure_date,
                        "inclusions": direction.inclusions,
                        "nodes": [
                            {
                                "id": node.id,
                                "iata": node.iata,
                                "city": node.city,
                                "layover_minutes": node.layover_minutes,
                            }
                            for node in direction.flight_nodes
                        ],
                    }
                    for direction in flight.directions
                ],
                hotels=[
                    {
                        "id": hotel.id,
                        "city": hotel.city,
                        "name": hotel.name,
                        "stars": hotel.stars,
                        "rating": hotel.rating,
                        "reviews_count": hotel.reviews_count,
                        "distance_text": hotel.distance_text,
                        "maps_url": hotel.maps_url,
                        "amenities": hotel.amenities,
                    }
                    for hotel in flight.tour.hotels
                ],
            )
            for flight in models
        ]

    async def get_tours_aggregates(
        self,
        from_date: datetime,
        to_date: datetime,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
    ) -> List[ToursAggregatesReadModel]:
        stmt = (
            select(
                FlightDirection.departure_date.label("date"),
                func.avg(Flights.price).label("avg_price"),
                func.min(Flights.price).label("min_price"),
                func.count(func.distinct(Flights.id)).label("tours_count"),
            )
            .join(Flights, Flights.id == FlightDirection.flight_id)
            .join(Tours, Tours.id == Flights.tour_id)
            .where(
                FlightDirection.direction == "outbound",
                FlightDirection.departure_date.between(from_date, to_date),
            )
        )
        
        # JOIN с таблицей availability для фильтрации по sold_out
        availability_alias = aliased(Availability)
        stmt = stmt.join(availability_alias, Flights.availability_status_id == availability_alias.id)
        stmt = stmt.where(availability_alias.value != 'sold_out')

        if tour_type is not None:
            # JOIN с таблицей tour_types для сравнения по value
            tour_type_alias = aliased(TourType)
            stmt = stmt.join(tour_type_alias, Tours.type_id == tour_type_alias.id)
            stmt = stmt.where(tour_type_alias.value == tour_type)

        if tarif is not None:
            # JOIN с таблицей tour_tarifs для сравнения по value
            tarif_alias = aliased(TourTarif)
            stmt = stmt.join(tarif_alias, Tours.tarif_id == tarif_alias.id)
            stmt = stmt.where(tarif_alias.value == tarif)

        if operator_id is not None:
            stmt = stmt.where(Tours.operator_id == operator_id)

        stmt = (
            stmt
            .group_by(FlightDirection.departure_date)
            .order_by(FlightDirection.departure_date)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            ToursAggregatesReadModel(
                date=row.date,
                avg_price=int(row.avg_price) if row.avg_price else 0,
                min_price=int(row.min_price) if row.min_price else 0,
                tours_count=int(row.tours_count) if row.tours_count else 0,
            ) for row in rows
        ]

    async def get_tour_tarifs(self) -> List[TourTarifReadModel]:
        stmt = select(TourTarif)

        result = await self.session.execute(stmt)
        models = result.scalars().unique().all()

        return [TourTarifReadModel(id=tarif.id, label=tarif.label) for tarif in models]

    async def get_tours_departure_cities(self) -> List[ToursDepartureCitiesReadModel]:
        stmt = select(DepartureCities)

        result = await self.session.execute(stmt)
        models = result.scalars().unique().all()

        return [ToursDepartureCitiesReadModel(id=tarif.id, label=tarif.label) for tarif in models]
