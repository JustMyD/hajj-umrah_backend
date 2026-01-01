from urllib.parse import quote_plus
from collections.abc import AsyncGenerator

from dynaconf import Dynaconf
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.core.common.unit_of_work import UnitOfWork
from src.infrastructure.common.db_unit_of_work import SqlAlchemyUnitOfWork


class DBProvider(Provider):
    """Провайдер подключения к БД."""

    def __init__(self) -> None:
        super().__init__()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def _build_async_url(self, settings: Dynaconf) -> str:
        """Приватный метод для построения URL"""
        safe_password = quote_plus(settings.DB_PASSWORD)
        return (
            f"postgresql+asyncpg://"
            f"{settings.DB_USER}:{safe_password}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}"
            f"/{settings.DB_NAME}"
        )

    @provide(scope=Scope.APP)
    def engine(self, settings: Dynaconf) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                self._build_async_url(settings),
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=settings.DB_POOL_PRE_PING,
            )
        return self._engine

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                engine, expire_on_commit=False, autoflush=False, autocommit=False
            )
        return self._session_factory

    @provide(scope=Scope.REQUEST)
    async def session(self, session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def sqlalchemy_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return SqlAlchemyUnitOfWork(session)
