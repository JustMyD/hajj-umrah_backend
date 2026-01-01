"""
Импорт всех моделей для регистрации в SQLAlchemy metadata.
Важно: все модели должны быть импортированы здесь, чтобы SQLAlchemy
могла правильно разрешить отношения между ними.
"""

from .base import Base
from .operator import Operators
from .tours import Tours
from .hotel import Hotels
from .flights import Flights, FlightDirection, FlightDirectionNodes
from .enums import Availability, TourType, TourTarif, Currency
from .users import Users, UserComparisons, UserFavorites
from .auth import AuthIdentities, MagicLinkTokens, EmailChangeTokens, RefreshTokens

__all__ = [
    "Base",
    "Operators",
    "Tours",
    "Hotels",
    "Flights",
    "FlightDirection",
    "FlightDirectionNodes",
    "Availability",
    "TourType",
    "TourTarif",
    "Currency",
    "Users",
    "UserComparisons",
    "UserFavorites",
    "AuthIdentities",
    "MagicLinkTokens",
    "EmailChangeTokens",
    "RefreshTokens",
]
