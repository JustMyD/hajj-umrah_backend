import logging
import logging.config
import uvicorn

from src.app import app
from src.infrastructure.di.providers.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    # Настройка логирования из конфига
    if hasattr(settings, "LOGGING") and settings.LOGGING:
        logging.config.dictConfig(settings.LOGGING)
    else:
        # Базовая настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Настройка uvicorn для логирования запросов
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s [%(levelname)s] %(message)s"
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s [%(levelname)s] %(client_addr)s - \"%(request_line)s\" %(status_code)s"
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_config=log_config,
        log_level="info",
    )
