import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from dishka.integrations.fastapi import setup_dishka

from src.infrastructure.di.container import create_container
from src.interfaces.http.routers.tour_router import tour_router
from src.interfaces.http.routers.operator_router import operators_router
from src.interfaces.http.routers.auth_router import auth_router
from src.interfaces.http.routers.user_router import user_router

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов и ответов."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Безопасно читаем body только если это не GET/HEAD/OPTIONS запрос
        body_str = ""
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            try:
                body = await request.body()
                body_str = f"| Body: {body.decode('utf-8')[:200]}" if body else ""
                # Восстанавливаем body для дальнейшей обработки
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except Exception:
                body_str = "| Body: <unable to read>"
        
        # Логируем входящий запрос
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"| Client: {request.client.host if request.client else 'unknown'} "
            f"| Query: {dict(request.query_params)}"
            f"{body_str}"
        )
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Вычисляем время выполнения
        process_time = time.time() - start_time
        
        # Логируем ответ
        logger.info(
            f"← {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.3f}s"
        )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Инициализация
    logger.info("✅ Application started")

    yield  # 🔸 приложение работает

    # 🔻 Завершение
    await app.container.close()
    logger.info("🛑 Application stopped")


def create_app() -> FastAPI:
    container = create_container()
    app = FastAPI(lifespan=lifespan)
    
    # Сохраняем контейнер для доступа в lifespan
    app.container = container
    
    # Настройка dishka должна быть до подключения роутеров
    setup_dishka(container, app)
    
    # Middleware для логирования запросов
    app.add_middleware(LoggingMiddleware)
    
    # CORS middleware ДОЛЖЕН быть добавлен последним, чтобы выполниться первым
    # (в FastAPI порядок выполнения middleware обратный порядку добавления)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Конкретный origin для поддержки credentials
        allow_credentials=True,  # Включаем поддержку credentials (cookies, authorization headers)
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Обработчик исключений для добавления CORS заголовков к ошибкам
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Обработчик всех исключений с добавлением CORS заголовков."""
        logger.exception(f"Unhandled exception: {exc}", exc_info=exc)
        
        # Создаем JSON ответ с ошибкой
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
        
        # Добавляем CORS заголовки вручную
        origin = request.headers.get("origin")
        if origin and origin == "http://localhost:3000":
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

    # Обработчик HTTP исключений (400, 401, 404 и т.д.)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Обработчик HTTP исключений с добавлением CORS заголовков."""
        response = JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
        
        # Добавляем CORS заголовки
        origin = request.headers.get("origin")
        if origin and origin == "http://localhost:3000":
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

    # Обработчик ошибок валидации
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Обработчик ошибок валидации с добавлением CORS заголовков."""
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
        
        # Добавляем CORS заголовки
        origin = request.headers.get("origin")
        if origin and origin == "http://localhost:3000":
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

    # Роуты для подключения
    app.include_router(tour_router)
    app.include_router(operators_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    
    return app


app = create_app()