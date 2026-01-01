from typing import TYPE_CHECKING, List

from sqlalchemy import String, Integer, Boolean, ForeignKey, Numeric, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList

from src.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.hotel import Hotels
    from src.infrastructure.db.models.flights import Flights
    from src.infrastructure.db.models.enums import TourType, TourTarif, Currency


class Tours(Base):
    __tablename__ = "tours"

    id: Mapped[int] = mapped_column(primary_key=True)

    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"))
    operator_name: Mapped[str] = mapped_column(String)
    operator_logo: Mapped[str] = mapped_column(String)
    operator_foundation_year: Mapped[int] = mapped_column(Integer)
    operator_verified: Mapped[bool] = mapped_column(Boolean)
    operator_features = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)

    title: Mapped[str] = mapped_column(String)
    type_id: Mapped[int] = mapped_column(ForeignKey("tour_types.id"), nullable=False)
    type: Mapped["TourType"] = relationship("TourType")

    price_amount: Mapped[float] = mapped_column(Numeric)
    price_currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"), nullable=False)
    price_currency: Mapped["Currency"] = relationship("Currency")

    duration: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String)

    visa_included: Mapped[bool] = mapped_column(Boolean)

    tarif_id: Mapped[int] = mapped_column(ForeignKey("tour_tarifs.id"), nullable=False)
    tarif: Mapped["TourTarif"] = relationship("TourTarif")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    hotels: Mapped[List["Hotels"]] = relationship(back_populates="tour")
    flights: Mapped[List["Flights"]] = relationship(back_populates="tour")

