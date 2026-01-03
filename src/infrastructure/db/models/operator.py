from typing import Optional

from sqlalchemy import String, Boolean, Integer, Column, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList

from src.infrastructure.db.models.base import Base

# if TYPE_CHECKING:
#     from src.infrastructure.db.models.tours import Tours


class Operators(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[str] = mapped_column(String, nullable=False)
    foundation_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True, default=None)  # рейтинг
    reviews_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)  # количество отзывов
    specialisations = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)  # бейджи специализации
    features = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)  # особенности
    certificates = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)  # сертификаты
    verified: Mapped[bool] = mapped_column(Boolean, default=False)  # аккредитация Хадж миссии РФ

    # tours: List["Tours"] = relationship(back_populates="operator")
