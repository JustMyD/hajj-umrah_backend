from typing import TYPE_CHECKING

from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList

from src.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.tours import Tours


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"))
    tour: Mapped["Tours"] = relationship(back_populates="hotels")

    city: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)

    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    reviews_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    distance_text: Mapped[str | None] = mapped_column(String, nullable=True)
    maps_url: Mapped[str | None] = mapped_column(String, nullable=True)

    amenities = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)
