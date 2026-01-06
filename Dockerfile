FROM python:3.11-slim

# Настройка DNS для решения проблем с сетью (опционально, можно удалить если не нужно)
# RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
#     echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Установка uv для управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Установка системных зависимостей
# Используем --network=host через build arg или настройки docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Копирование исходного кода
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Порт приложения
EXPOSE 8000

RUN chmod +x apply_migrations.sh

CMD ["./apply_migrations.sh"]