from urllib.parse import quote_plus

from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.yml"],
    environments=True,
    env_switcher="ENV_FOR_DYNACONF",
    load_dotenv=True,
    dotenv_path=".env",
    merge_enabled=True,
)


def get_sync_db_url() -> str:
    """
    Подключение для синхронного драйвера (psycopg3)
    """
    safe_password = quote_plus(settings.DB_PASSWORD)
    return (
        f"postgresql+psycopg://"
        f"{settings.DB_USER}:{safe_password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}"
        f"/{settings.DB_NAME}"
    )


def get_settings() -> Dynaconf:
    """Доступ к конфигурации приложения (один объект для всего проекта)."""
    return settings


class ConfigProvider(Provider):
    """DI-провайдер конфигурации приложения."""

    def __init__(self) -> None:
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def settings(self) -> Dynaconf:
        """Провайдер единственного объекта конфигурации."""
        return self._settings

