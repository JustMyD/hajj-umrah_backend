from collections.abc import Iterable
from typing import Optional

from dishka import Provider, make_async_container

from src.infrastructure.di.providers.config import ConfigProvider
from src.infrastructure.di.providers.db_provider import DBProvider
from src.infrastructure.di.providers.tour import TourProvider
from src.infrastructure.di.providers.operator import OperatorProvider
from src.infrastructure.di.providers.user import UserProvider
from src.infrastructure.di.providers.auth import AuthProvider


def create_container(providers: Optional[Iterable[Provider]] = None):
    """Фабрика контейнера DI с дефолтным набором провайдеров."""
    provider_list = (
        list(providers)
        if providers is not None
        else [
            ConfigProvider(),
            DBProvider(),
            TourProvider(),
            OperatorProvider(),
            UserProvider(),
            AuthProvider(),
        ]
    )
    return make_async_container(*provider_list)

