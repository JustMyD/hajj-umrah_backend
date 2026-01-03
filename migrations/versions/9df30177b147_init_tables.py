"""init_tables

Revision ID: 9df30177b147
Revises: 
Create Date: 2025-12-14 18:29:47.008504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


# revision identifiers, used by Alembic.
revision: str = '9df30177b147'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Названия enum типов
TOUR_TYPE_ENUM_NAME = 'tour_type'
TOUR_TARIFS_ENUM_NAME = 'tour_tarifs'
PRICE_CURRENCIES_ENUM_NAME = 'price_currencies'
FLIGHT_AVAILABILITY_STATUSES_ENUM_NAME = 'flight_availability_statuses'


def upgrade() -> None:
    """Upgrade schema."""
    # Таблица доступности вылета
    op.create_table(
        'availability',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False, unique=True),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица типов туров
    op.create_table(
        'tour_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False, unique=True),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица тарифов туров
    op.create_table(
        'tour_tarifs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False, unique=True),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица валют
    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False, unique=True),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Таблица города отправлений
    op.create_table(
        'departure_cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False, unique=True),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Заполнение таблиц перечислений данными
    availability_table = sa.table(
        'availability',
        sa.column('value', sa.String),
        sa.column('label', sa.String)
    )
    op.bulk_insert(availability_table, [
        {'value': 'available', 'label': 'Доступен'},
        {'value': 'limited', 'label': 'Ограниченная доступность'},
        {'value': 'sold_out', 'label': 'Распродан'},
    ])
    
    tour_types_table = sa.table(
        'tour_types',
        sa.column('value', sa.String),
        sa.column('label', sa.String)
    )
    op.bulk_insert(tour_types_table, [
        {'value': 'umrah', 'label': 'Умра'},
        {'value': 'hajj', 'label': 'Хадж'},
        {'value': 'all', 'label': 'Все'},
    ])
    
    tour_tarifs_table = sa.table(
        'tour_tarifs',
        sa.column('value', sa.String),
        sa.column('label', sa.String)
    )
    op.bulk_insert(tour_tarifs_table, [
        {'value': 'budget', 'label': 'Бюджет'},
        {'value': 'standard', 'label': 'Стандарт'},
        {'value': 'comfort', 'label': 'Комфорт'},
        {'value': 'premium', 'label': 'Премиум'},
    ])
    
    currencies_table = sa.table(
        'currencies',
        sa.column('value', sa.String),
        sa.column('label', sa.String)
    )
    op.bulk_insert(currencies_table, [
        {'value': 'dollar', 'label': 'Доллар'},
        {'value': 'rubles', 'label': 'Рубли'},
    ])
    
    # Таблица туроператоров
    op.create_table(
        'operators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('logo', sa.String(), nullable=False),
        sa.Column('foundation_year', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Numeric(), nullable=True),
        sa.Column('reviews_count', sa.Integer(), nullable=True),
        sa.Column('specialisations', JSONB(), nullable=False),
        sa.Column('features', JSONB(), nullable=False),
        sa.Column('certificates', JSONB(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица туров
    op.create_table(
        'tours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=False),
        sa.Column('operator_name', sa.String(), nullable=False),
        sa.Column('operator_logo', sa.String(), nullable=False),
        sa.Column('operator_foundation_year', sa.Integer(), nullable=False),
        sa.Column('operator_verified', sa.Boolean(), nullable=False),
        sa.Column('operator_features', JSONB(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('price_amount', sa.Numeric(), nullable=False),
        sa.Column('price_currency_id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('visa_included', sa.Boolean(), nullable=False),
        sa.Column('tarif_id', sa.Integer(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ),
        sa.ForeignKeyConstraint(['type_id'], ['tour_types.id'], ),
        sa.ForeignKeyConstraint(['price_currency_id'], ['currencies.id'], ),
        sa.ForeignKeyConstraint(['tarif_id'], ['tour_tarifs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица отелей
    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tour_id', sa.Integer(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('stars', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('reviews_count', sa.Integer(), nullable=True),
        sa.Column('distance_text', sa.String(), nullable=True),
        sa.Column('maps_url', sa.String(), nullable=True),
        sa.Column('amenities', JSONB(), nullable=False),
        sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица вылетов
    op.create_table(
        'flights',
        sa.Column('id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('tour_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(), nullable=False),
        sa.Column('availability_status_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
        sa.ForeignKeyConstraint(['availability_status_id'], ['availability.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица направлений перелетов
    op.create_table(
        'flight_directions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('direction', sa.String(), nullable=False),
        sa.Column('inclusions', JSONB(), nullable=False),
        sa.Column('departure_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Таблица узлов перелетов (пересадок)
    op.create_table(
        'flight_layovers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_direction_id', sa.Integer(), nullable=False),
        sa.Column('iata', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('layover_minutes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['flight_direction_id'], ['flight_directions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # =========================
    # Users / Auth (MVP)
    # =========================
    op.create_table(
        "users",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("surname", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("email_notification", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sms_notification", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    # Уникальность только для непустых email (Postgres partial unique index)
    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("email IS NOT NULL"),
    )

    op.create_table(
        "auth_identities",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_account_id", sa.String(), nullable=False),
        sa.Column("email_at_provider", sa.String(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"], unique=False)
    op.create_index(
        "ux_auth_identities_provider_account",
        "auth_identities",
        ["provider", "provider_account_id"],
        unique=True,
    )

    op.create_table(
        "magic_link_tokens",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_ip", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_magic_link_tokens_email", "magic_link_tokens", ["email"], unique=False)
    op.create_index("ix_magic_link_tokens_expires_at", "magic_link_tokens", ["expires_at"], unique=False)
    op.create_index("ix_magic_link_tokens_created_at", "magic_link_tokens", ["created_at"], unique=False)
    op.create_index("ux_magic_link_tokens_hash", "magic_link_tokens", ["token_hash"], unique=True)

    op.create_table(
        "email_change_tokens",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("new_email", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_ip", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_change_tokens_user_id", "email_change_tokens", ["user_id"], unique=False)
    op.create_index("ix_email_change_tokens_new_email", "email_change_tokens", ["new_email"], unique=False)
    op.create_index("ix_email_change_tokens_expires_at", "email_change_tokens", ["expires_at"], unique=False)
    op.create_index("ix_email_change_tokens_created_at", "email_change_tokens", ["created_at"], unique=False)
    op.create_index("ux_email_change_tokens_hash", "email_change_tokens", ["token_hash"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", PG_UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_ip", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False)
    op.create_index("ix_refresh_tokens_created_at", "refresh_tokens", ["created_at"], unique=False)
    op.create_index("ux_refresh_tokens_hash", "refresh_tokens", ["token_hash"], unique=True)

    # Таблица избранных туров
    op.create_table(
        'user_favorites',
        sa.Column('user_id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('tour_id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tour_id'], ['flights.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'tour_id')
    )

    # Индексы для user_favorites
    op.create_index('ix_user_favorites_user_id', 'user_favorites', ['user_id'], unique=False)
    op.create_index('ix_user_favorites_tour_id', 'user_favorites', ['tour_id'], unique=False)

    # Таблица сравнения туров
    op.create_table(
        'user_comparisons',
        sa.Column('user_id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('tour_id', PG_UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tour_id'], ['flights.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'tour_id')
    )

    # Индексы для user_comparisons
    op.create_index('ix_user_comparisons_user_id', 'user_comparisons', ['user_id'], unique=False)
    op.create_index('ix_user_comparisons_tour_id', 'user_comparisons', ['tour_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаление индексов и таблиц в обратном порядке
    op.drop_index('ix_user_comparisons_tour_id', table_name='user_comparisons')
    op.drop_index('ix_user_comparisons_user_id', table_name='user_comparisons')
    op.drop_table('user_comparisons')

    op.drop_index('ix_user_favorites_tour_id', table_name='user_favorites')
    op.drop_index('ix_user_favorites_user_id', table_name='user_favorites')
    op.drop_table('user_favorites')

    op.drop_index("ux_email_change_tokens_hash", table_name="email_change_tokens")
    op.drop_index("ix_email_change_tokens_created_at", table_name="email_change_tokens")
    op.drop_index("ix_email_change_tokens_expires_at", table_name="email_change_tokens")
    op.drop_index("ix_email_change_tokens_new_email", table_name="email_change_tokens")
    op.drop_index("ix_email_change_tokens_user_id", table_name="email_change_tokens")
    op.drop_table("email_change_tokens")

    op.drop_index("ux_refresh_tokens_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_created_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ux_magic_link_tokens_hash", table_name="magic_link_tokens")
    op.drop_index("ix_magic_link_tokens_created_at", table_name="magic_link_tokens")
    op.drop_index("ix_magic_link_tokens_expires_at", table_name="magic_link_tokens")
    op.drop_index("ix_magic_link_tokens_email", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")

    op.drop_index("ux_auth_identities_provider_account", table_name="auth_identities")
    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_table("auth_identities")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table('flight_layovers')
    op.drop_table('flight_directions')
    op.drop_table('flights')
    op.drop_table('hotels')
    op.drop_table('tours')
    op.drop_table('operators')
    
    # Удаление таблиц перечислений
    op.drop_table('currencies')
    op.drop_table('tour_tarifs')
    op.drop_table('tour_types')
    op.drop_table('availability')
    op.drop_table('departure_cities')
