#!/usr/bin/env bash
set -e

echo "🚀 Starting backend container"

echo "⏳ Running Alembic migrations..."
uv run alembic upgrade head

echo "✅ Migrations applied"

echo "🔥 Starting application"
exec uv run python start_app.py
