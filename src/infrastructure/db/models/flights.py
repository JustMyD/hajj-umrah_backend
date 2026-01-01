from uuid import UUID
from typing import TYPE_CHECKING, List
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.mutable import MutableList

from src.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.tours import Tours
    from src.infrastructure.db.models.enums import Availability
    from src.infrastructure.db.models.users import UserFavorites, UserComparisons


class Flights(Base):
    __tablename__ = "flights"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"))
    tour: Mapped["Tours"] = relationship(back_populates="flights")

    price: Mapped[float] = mapped_column(Numeric)
    directions: Mapped[List["FlightDirection"]] = relationship(back_populates="flight")

    availability_status_id: Mapped[int] = mapped_column(ForeignKey("availability.id"), nullable=False)
    availability_status: Mapped["Availability"] = relationship("Availability")

    favorited_by: Mapped[list["UserFavorites"]] = relationship(back_populates="tour", cascade="all, delete-orphan")
    compared_by: Mapped[list["UserComparisons"]] = relationship(back_populates="tour", cascade="all, delete-orphan")


class FlightDirection(Base):
    __tablename__ = "flight_directions"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_id: Mapped[UUID] = mapped_column(ForeignKey("flights.id"))
    flight: Mapped["Flights"] = relationship(back_populates="directions")
    direction: Mapped[str] = mapped_column(String, nullable=False) # Описывает направление outbound/inbound например

    inclusions = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)

    departure_date: Mapped[datetime] = mapped_column(DateTime)

    # Точки перелета
    flight_nodes: Mapped[List["FlightDirectionNodes"]] = relationship(back_populates="flight_direction")


class FlightDirectionNodes(Base):
    __tablename__ = "flight_layovers"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Связь с направлением перелета
    flight_direction_id: Mapped[int] = mapped_column(ForeignKey("flight_directions.id"))
    flight_direction: Mapped[FlightDirection] = relationship(back_populates="flight_nodes")

    iata: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    layover_minutes: Mapped[int] = mapped_column(Integer)
