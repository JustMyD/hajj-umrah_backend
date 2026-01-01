from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.flights import Flights


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)

    email: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))

    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    surname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    email_notification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sms_notification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    favorites: Mapped[List["UserFavorites"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorite_tours: Mapped[List["Flights"]] = relationship(secondary="user_favorites", viewonly=True)

    comparisons: Mapped[List["UserComparisons"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    compared_tours: Mapped[List["Flights"]] = relationship(secondary="user_comparisons", viewonly=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class UserFavorites(Base):
    __tablename__ = "user_favorites"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tour_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("flights.id", ondelete="CASCADE"), primary_key=True)  # Ссылаемся на конкретные вылеты
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    user: Mapped[Users] = relationship(back_populates="favorites")
    tour: Mapped["Flights"] = relationship(back_populates="favorited_by")


class UserComparisons(Base):
    __tablename__ = "user_comparisons"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tour_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("flights.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    user: Mapped[Users] = relationship(back_populates="comparisons")
    tour: Mapped["Flights"] = relationship(back_populates="compared_by")
