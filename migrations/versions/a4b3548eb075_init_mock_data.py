"""init_mock_data

Revision ID: a4b3548eb075
Revises: 9df30177b147
Create Date: 2025-12-15 18:44:09.842235

"""
import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

# Добавляем путь к utils для импорта генератора данных
migrations_dir = Path(__file__).parent.parent
sys.path.insert(0, str(migrations_dir.parent))

from migrations.utils.mock_data_generator import generate_mock_data, NUM_OPERATORS, RUSSIAN_CITIES

# Названия enum типов (должны совпадать с init_tables.py)
TOUR_TYPE_ENUM_NAME = 'tour_type'
TOUR_TARIFS_ENUM_NAME = 'tour_tarifs'
PRICE_CURRENCIES_ENUM_NAME = 'price_currencies'
FLIGHT_AVAILABILITY_STATUSES_ENUM_NAME = 'flight_availability_statuses'


# revision identifiers, used by Alembic.
revision: str = 'a4b3548eb075'
down_revision: Union[str, None] = '9df30177b147'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Заполнение базы данных мок-данными."""
    # Генерируем мок-данные
    # Количество туров на оператора: 3-5 (случайно)
    # Отелей на тур: всегда 2 (Мекка и Медина)
    # Вылетов: 4-5 в месяц с декабря 2025 до июля 2026
    # Пересадок: 0 или 1 на каждое направление (случайно)
    mock_data = generate_mock_data(num_operators=NUM_OPERATORS)
    
    bind = op.get_bind()
    
    # Вставка городов отправлений (российские города)
    if RUSSIAN_CITIES:
        # Получаем уникальные города (убираем дубликаты по названию города)
        unique_cities = {}
        for iata, city in RUSSIAN_CITIES:
            if city not in unique_cities:
                unique_cities[city] = iata
        
        # Формируем данные для вставки
        departure_cities_data = []
        for idx, (city, iata) in enumerate(unique_cities.items(), start=1):
            departure_cities_data.append({
                'id': idx,
                'value': iata.lower(),  # Используем IATA код в нижнем регистре как value
                'label': city,  # Название города как label
            })
        
        departure_cities_table = sa.table('departure_cities',
            sa.column('id', sa.Integer),
            sa.column('value', sa.String),
            sa.column('label', sa.String),
        )
        op.bulk_insert(departure_cities_table, departure_cities_data)
    
    # Вставка операторов
    if mock_data['operators']:
        operators_table = sa.table('operators',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('logo', sa.String),
            sa.column('foundation_year', sa.Integer),
            sa.column('rating', sa.Numeric),
            sa.column('reviews_count', sa.Integer),
            sa.column('specialisations', JSONB),
            sa.column('features', JSONB),
            sa.column('certificates', JSONB),
            sa.column('verified', sa.Boolean),
        )
        op.bulk_insert(operators_table, mock_data['operators'])
    
    # Вставка туров
    if mock_data['tours']:
        # Получаем ID из таблиц перечислений для преобразования строковых значений
        tour_types_map = {row[1]: row[0] for row in bind.execute(sa.text("SELECT id, value FROM tour_types")).fetchall()}
        currencies_map = {row[1]: row[0] for row in bind.execute(sa.text("SELECT id, value FROM currencies")).fetchall()}
        tour_tarifs_map = {row[1]: row[0] for row in bind.execute(sa.text("SELECT id, value FROM tour_tarifs")).fetchall()}
        
        # Преобразуем строковые значения в ID
        tours_data = []
        for tour in mock_data['tours']:
            tour_data = tour.copy()
            tour_data['type_id'] = tour_types_map.get(tour.get('type'), None)
            tour_data['price_currency_id'] = currencies_map.get(tour.get('price_currency'), None)
            tour_data['tarif_id'] = tour_tarifs_map.get(tour.get('tarif'), None)
            # Удаляем старые строковые поля
            tour_data.pop('type', None)
            tour_data.pop('price_currency', None)
            tour_data.pop('tarif', None)
            tours_data.append(tour_data)
        
        tours_table = sa.table('tours',
            sa.column('id', sa.Integer),
            sa.column('operator_id', sa.Integer),
            sa.column('operator_name', sa.String),
            sa.column('operator_logo', sa.String),
            sa.column('operator_foundation_year', sa.Integer),
            sa.column('operator_verified', sa.Boolean),
            sa.column('operator_features', JSONB),
            sa.column('title', sa.String),
            sa.column('type_id', sa.Integer),
            sa.column('price_amount', sa.Numeric),
            sa.column('price_currency_id', sa.Integer),
            sa.column('duration', sa.Integer),
            sa.column('location', sa.String),
            sa.column('visa_included', sa.Boolean),
            sa.column('tarif_id', sa.Integer),
            sa.column('is_published', sa.Boolean),
        )
        op.bulk_insert(tours_table, tours_data)
    
    # Вставка отелей
    if mock_data['hotels']:
        hotels_table = sa.table('hotels',
            sa.column('id', sa.Integer),
            sa.column('tour_id', sa.Integer),
            sa.column('city', sa.String),
            sa.column('name', sa.String),
            sa.column('stars', sa.Integer),
            sa.column('rating', sa.Float),
            sa.column('reviews_count', sa.Integer),
            sa.column('distance_text', sa.String),
            sa.column('maps_url', sa.String),
            sa.column('amenities', JSONB),
        )
        op.bulk_insert(hotels_table, mock_data['hotels'])
    
    # Вставка вылетов
    if mock_data['flights']:
        # Получаем ID из таблицы availability для преобразования строковых значений
        availability_map = {row[1]: row[0] for row in bind.execute(sa.text("SELECT id, value FROM availability")).fetchall()}
        
        # Преобразуем строковые значения в ID
        flights_data = []
        for flight in mock_data['flights']:
            flight_data = flight.copy()
            flight_data['availability_status_id'] = availability_map.get(flight.get('availability_status'), None)
            # Удаляем старое строковое поле
            flight_data.pop('availability_status', None)
            flights_data.append(flight_data)
        
        flights_table = sa.table('flights',
            sa.column('id', PG_UUID),
            sa.column('tour_id', sa.Integer),
            sa.column('price', sa.Numeric),
            sa.column('availability_status_id', sa.Integer),
        )
        op.bulk_insert(flights_table, flights_data)
    
    # Вставка направлений перелетов (после flights, так как flight_directions ссылается на flights.id)
    if mock_data['flight_directions']:
        flight_directions_table = sa.table('flight_directions',
            sa.column('id', sa.Integer),
            sa.column('flight_id', PG_UUID),
            sa.column('direction', sa.String),
            sa.column('inclusions', JSONB),
            sa.column('departure_date', sa.DateTime),
        )
        op.bulk_insert(flight_directions_table, mock_data['flight_directions'])
    
    # Вставка узлов перелетов
    if mock_data['flight_layovers']:
        flight_layovers_table = sa.table('flight_layovers',
            sa.column('id', sa.Integer),
            sa.column('flight_direction_id', sa.Integer),
            sa.column('iata', sa.String),
            sa.column('city', sa.String),
            sa.column('layover_minutes', sa.Integer),
        )
        op.bulk_insert(flight_layovers_table, mock_data['flight_layovers'])


def downgrade() -> None:
    """Удаление мок-данных из базы данных."""
    # Удаляем данные в обратном порядке (сначала зависимые таблицы)
    op.execute("DELETE FROM flight_layovers")
    op.execute("DELETE FROM flight_directions")
    op.execute("DELETE FROM flights")
    op.execute("DELETE FROM hotels")
    op.execute("DELETE FROM tours")
    op.execute("DELETE FROM operators")
    op.execute("DELETE FROM departure_cities")
