"""
Модели для таблиц перечислений (enum-like tables).
Каждая таблица содержит техническое значение и человеко-читаемое значение для фронтенда.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class Availability(Base):
    """Таблица доступности вылета."""
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Техническое значение: 'available', 'limited', 'sold_out'
    label: Mapped[str] = mapped_column(String, nullable=False)  # Человеко-читаемое значение для фронтенда


class TourType(Base):
    """Таблица типов туров."""
    __tablename__ = "tour_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Техническое значение: 'umrah', 'hajj', 'all'
    label: Mapped[str] = mapped_column(String, nullable=False)  # Человеко-читаемое значение для фронтенда


class TourTarif(Base):
    """Таблица тарифов туров."""
    __tablename__ = "tour_tarifs"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Техническое значение: 'budget', 'standard', 'comfort', 'premium'
    label: Mapped[str] = mapped_column(String, nullable=False)  # Человеко-читаемое значение для фронтенда


class Currency(Base):
    """Таблица валют."""
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Техническое значение: 'dollar', 'rubles'
    label: Mapped[str] = mapped_column(String, nullable=False)  # Человеко-читаемое значение для фронтенда


class DepartureCities(Base):
    """Таблица городов отправлений."""
    __tablename__ = "departure_cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
