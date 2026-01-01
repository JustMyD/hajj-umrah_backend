"""
Генератор мок-данных для заполнения базы данных.
Используется в миграциях Alembic для создания тестовых данных.
"""
import random
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any, Tuple

# ============================================================================
# ПУСТЫЕ СПИСКИ ДЛЯ ДАННЫХ (заполняются пользователем)
# ============================================================================

NUM_OPERATORS = 7

# Данные для туроператоров
OPERATOR_NAMES: List[str] = [
    "Аль-Хадж Тур",
    "Медина Тревел",
    "Святые Земли",
    "Паломник Тур",
    "Мекка Тревел",
    "Исламские Туры",
    "Хадж Экспресс",
    "Умра Плюс",
    "Священное Путешествие",
    "Аль-Кааба Тур",
    "Паломнические Туры",
    "Мекка Медина Тур",
    "Хадж Сервис",
    "Умра Тур",
    "Святые Места",
]

OPERATOR_DESCRIPTIONS: List[str] = [
    "Опытный туроператор с многолетней историей организации паломнических туров",
    "Профессиональная организация хаджа и умры с полным сопровождением",
    "Надежный партнер для паломнических поездок в Мекку и Медину",
    "Компания с аккредитацией Хадж миссии РФ, специализирующаяся на религиозном туризме",
    "Организация паломнических туров с соблюдением всех религиозных требований",
    "Туроператор с большим опытом работы в сфере религиозного туризма",
    "Профессиональное сопровождение паломников в священные города",
    "Организация комфортных и безопасных паломнических поездок",
    "Туроператор с проверенной репутацией в организации хаджа и умры",
    "Специализация на паломнических турах с полным сервисом",
]

OPERATOR_LOGOS: List[str] = [
    f"logo_{i}.png" for i in range(0, NUM_OPERATORS)  # Генерируем названия логотипов
]

OPERATOR_SPECIALISATIONS: List[str] = [
    "Хадж",
    "Умра",
    "VIP туры",
    "Групповые туры",
    "Индивидуальные туры",
    "Экономичные туры",
    "Премиум туры",
    "Семейные туры",
]

OPERATOR_FEATURES: List[str] = [
    "Опытные гиды-мутавифы",
    "Трансфер из аэропорта",
    "Питание включено",
    "Проживание рядом с мечетью",
    "Медицинское сопровождение",
    "Виза включена",
    "Групповые молитвы",
    "Образовательные программы",
    "Круглосуточная поддержка",
    "Организация жертвоприношения",
    "Помощь в оформлении документов",
    "Русскоязычное сопровождение",
]

OPERATOR_CERTIFICATES: List[str] = [
    "Аккредитация Хадж миссии РФ",
    "Сертификат качества ISO",
    "Лицензия туроператора",
    "Сертификат безопасности",
    "Награда лучший туроператор года",
]

# Данные для туров
TOUR_TITLES: List[str] = [
    "Умра в месяц Рамадан",
    "Хадж 2026 - Полный пакет",
    "Умра для начинающих",
    "Премиум Хадж",
    "Экономичная Умра",
    "Семейная Умра",
    "Хадж с комфортом",
    "Умра в священный месяц",
    "Классический Хадж",
    "Умра выходного дня",
    "Хадж с VIP сервисом",
    "Умра для пожилых",
    "Групповая Умра",
    "Хадж с образовательной программой",
    "Умра в Раджаб",
]

TOUR_LOCATIONS: List[str] = [
    "Мекка, Медина",
    "Мекка",
    "Медина, Мекка",
    "Священные города",
    "Мекка и Медина",
]

# Данные для отелей
# Отели всегда в двух городах: Мекка и Медина
HOTEL_NAMES_MAKKAH: List[str] = [
    "Отель Аль-Харам",
    "Мекка Гранд Отель",
    "Отель Дар Аль-Иман",
    "Мекка Плаза",
    "Отель Аль-Кааба",
    "Мекка Тауэр",
    "Отель Аль-Мадина",
    "Мекка Резорт",
    "Отель Аль-Сафа",
    "Мекка Хилтон",
    "Отель Аль-Марва",
    "Мекка Интерконтиненталь",
    "Отель Аль-Абрадж",
    "Мекка Шератон",
    "Отель Аль-Байт",
]

HOTEL_NAMES_MADINAH: List[str] = [
    "Отель Аль-Масджид Ан-Набави",
    "Медина Гранд Отель",
    "Отель Дар Аль-Хиджра",
    "Медина Плаза",
    "Отель Аль-Мансур",
    "Медина Тауэр",
    "Отель Аль-Ансар",
    "Медина Резорт",
    "Отель Аль-Кибла",
    "Медина Хилтон",
    "Отель Аль-Муджтаба",
    "Медина Интерконтиненталь",
    "Отель Аль-Баки",
    "Медина Шератон",
    "Отель Аль-Кудс",
]

HOTEL_AMENITIES: List[str] = [
    "Wi-Fi",
    "Кондиционер",
    "Мини-бар",
    "Сейф",
    "Телевизор",
    "Холодильник",
    "Чайник",
    "Фен",
    "Халат и тапочки",
    "Вид на мечеть",
    "Молитвенный коврик",
    "Компас Киблы",
    "Коран в номере",
    "Балкон",
    "Ресторан",
    "Спа-центр",
    "Тренажерный зал",
    "Бассейн",
    "Парковка",
    "Трансфер до мечети",
]

# Данные для перелетов
# Российские города (для вылета и прилета)
RUSSIAN_CITIES: List[Tuple[str, str]] = [
    ("DME", "Москва"),  # Москва Домодедово
    ("SVO", "Москва"),  # Москва Шереметьево
    ("VKO", "Москва"),  # Москва Внуково
    ("LED", "Санкт-Петербург"),  # Санкт-Петербург
    ("KZN", "Казань"),  # Казань
    ("UFA", "Уфа"),  # Уфа
    ("AER", "Сочи"),  # Сочи
    ("ROV", "Ростов-на-Дону"),  # Ростов-на-Дону
    ("MCX", "Махачкала"),  # Махачкала
    ("GRV", "Грозный"),  # Грозный
    ("ASF", "Астрахань"),  # Астрахань
    ("MRV", "Минеральные Воды"),  # Минеральные Воды
]

# Города Саудовской Аравии (для прилета и вылета)
SAUDI_CITIES: List[Tuple[str, str]] = [
    ("JED", "Джидда"),  # Джидда (основной аэропорт для Мекки)
    ("MED", "Медина"),  # Медина
    ("RUH", "Эр-Рияд"),  # Эр-Рияд
]

# Города для пересадок (Турция, Персидский залив, Кавказ)
LAYOVER_CITIES: List[Tuple[str, str]] = [
    ("IST", "Стамбул"),  # Стамбул (Турция)
    ("SAW", "Стамбул"),  # Стамбул Сабиха Гёкчен (Турция)
    ("DXB", "Дубай"),  # Дубай (ОАЭ)
    ("AUH", "Абу-Даби"),  # Абу-Даби (ОАЭ)
    ("DOH", "Доха"),  # Доха (Катар)
    ("BAH", "Манама"),  # Манама (Бахрейн)
    ("KWI", "Эль-Кувейт"),  # Эль-Кувейт (Кувейт)
    ("MCT", "Маскат"),  # Маскат (Оман)
    ("GYD", "Баку"),  # Баку (Азербайджан)
    ("EVN", "Ереван"),  # Ереван (Армения)
    ("TBS", "Тбилиси"),  # Тбилиси (Грузия)
]

FLIGHT_INCLUSIONS: List[str] = [
    "Питание на борту",
    "Багаж 20 кг",
    "Багаж 30 кг",
    "Развлечения на борту",
    "Wi-Fi на борту",
    "Дополнительное место",
    "Приоритетная посадка",
    "Бизнес-класс",
    "Комфорт-класс",
    "Дополнительное питание",
]

# ============================================================================
# ФУНКЦИИ ГЕНЕРАЦИИ ДАННЫХ
# ============================================================================


def get_random_item(items: List[Any]) -> Any:
    """Получить случайный элемент из списка."""
    if not items:
        raise ValueError(f"Список {items} пуст. Заполните данные перед использованием.")
    return random.choice(items)


def get_random_items(items: List[Any], count: int, allow_duplicates: bool = True) -> List[Any]:
    """Получить случайные элементы из списка."""
    if not items:
        raise ValueError(f"Список {items} пуст. Заполните данные перед использованием.")
    if allow_duplicates:
        return [random.choice(items) for _ in range(count)]
    else:
        return random.sample(items, min(count, len(items)))


def generate_operator_data(
    operator_id: int,
    available_logos: List[str],
    available_names: List[str],
    available_descriptions: List[str]
) -> Tuple[Dict[str, Any], List[str], List[str], List[str]]:
    """
    Генерирует данные для одного туроператора.
    
    Args:
        operator_id: ID оператора
        available_logos: Список доступных логотипов (будет изменен - использованный логотип удаляется)
        available_names: Список доступных названий (будет изменен - использованное название удаляется)
        available_descriptions: Список доступных описаний (будет изменен - использованное описание удаляется)
    
    Returns:
        Кортеж (данные оператора, обновленный список логотипов, обновленный список названий, обновленный список описаний)
    """
    foundation_year = random.randint(1990, 2020)
    
    # Генерируем массивы из списков: выбираем случайное количество элементов
    num_specialisations = random.randint(1, min(3, len(OPERATOR_SPECIALISATIONS))) if OPERATOR_SPECIALISATIONS else 0
    num_features = random.randint(1, min(5, len(OPERATOR_FEATURES))) if OPERATOR_FEATURES else 0
    num_certificates = random.randint(0, min(3, len(OPERATOR_CERTIFICATES))) if OPERATOR_CERTIFICATES else 0
    
    # Выбираем и удаляем логотип из списка, чтобы не было повторений
    if not available_logos:
        raise ValueError("Недостаточно логотипов для всех операторов. Добавьте больше логотипов в OPERATOR_LOGOS.")
    logo = random.choice(available_logos)
    available_logos.remove(logo)
    
    # Выбираем и удаляем название из списка, чтобы не было повторений
    if not available_names:
        raise ValueError("Недостаточно названий для всех операторов. Добавьте больше названий в OPERATOR_NAMES.")
    name = random.choice(available_names)
    available_names.remove(name)
    
    # Выбираем и удаляем описание из списка, чтобы не было повторений
    if not available_descriptions:
        raise ValueError("Недостаточно описаний для всех операторов. Добавьте больше описаний в OPERATOR_DESCRIPTIONS.")
    description = random.choice(available_descriptions)
    available_descriptions.remove(description)
    
    operator_data = {
        'id': operator_id,
        'name': name,
        'description': description,
        'logo': logo,
        'foundation_year': foundation_year,
        'rating': round(random.uniform(3.5, 5.0), 2),
        'reviews_count': random.randint(10, 10000),
        'specialisations': get_random_items(OPERATOR_SPECIALISATIONS, num_specialisations, allow_duplicates=False) if OPERATOR_SPECIALISATIONS else [],
        'features': get_random_items(OPERATOR_FEATURES, num_features, allow_duplicates=False) if OPERATOR_FEATURES else [],
        'certificates': get_random_items(OPERATOR_CERTIFICATES, num_certificates, allow_duplicates=False) if OPERATOR_CERTIFICATES else [],
        'verified': random.choice([True, False]),
    }
    
    return operator_data, available_logos, available_names, available_descriptions


def generate_tour_data(tour_id: int, operator_id: int, operator_data: Dict[str, Any]) -> Dict[str, Any]:
    """Генерирует данные для одного тура."""
    tour_types = ['umrah', 'hajj']
    tarifs = ['budget', 'standard', 'comfort', 'premium']
    currencies = ['dollar', 'rubles']
    
    return {
        'id': tour_id,
        'operator_id': operator_id,
        'operator_name': operator_data['name'],
        'operator_logo': operator_data['logo'],
        'operator_foundation_year': operator_data['foundation_year'],
        'operator_verified': operator_data['verified'],
        'operator_features': operator_data['features'],
        'title': get_random_item(TOUR_TITLES) if TOUR_TITLES else f"Тур #{tour_id}",
        'type': random.choice(tour_types),
        'price_amount': round(random.uniform(500, 5000), 2),
        'price_currency': random.choice(currencies),
        'duration': random.randint(7, 30),
        'location': get_random_item(TOUR_LOCATIONS) if TOUR_LOCATIONS else "Мекка, Медина",
        'visa_included': random.choice([True, False]),
        'tarif': random.choice(tarifs),
        'is_published': random.choice([True, False]),
    }


def generate_hotel_data(hotel_id: int, tour_id: int, city: str) -> Dict[str, Any]:
    """
    Генерирует данные для одного отеля.
    
    Args:
        hotel_id: ID отеля
        tour_id: ID тура
        city: Город отеля ('Мекка' или 'Медина')
    """
    if city == 'Мекка':
        hotel_name = get_random_item(HOTEL_NAMES_MAKKAH) if HOTEL_NAMES_MAKKAH else f"Отель в Мекке #{hotel_id}"
    elif city == 'Медина':
        hotel_name = get_random_item(HOTEL_NAMES_MADINAH) if HOTEL_NAMES_MADINAH else f"Отель в Медине #{hotel_id}"
    else:
        raise ValueError(f"Неизвестный город: {city}. Допустимые значения: 'Мекка', 'Медина'")
    
    return {
        'id': hotel_id,
        'tour_id': tour_id,
        'city': city,
        'name': hotel_name,
        'stars': random.choice([None, 3, 4, 5]),
        'rating': round(random.uniform(3.0, 5.0), 2),
        'reviews_count': random.randint(5, 5000),
        'distance_text': random.choice(["500 м от мечети", "1 км от мечети", "2 км от мечети", "300 метров от мечети", "500 метров от мечети"]),
        'maps_url': f"https://maps.example.com/hotel/{hotel_id}",
        'amenities': get_random_items(HOTEL_AMENITIES, random.randint(2, min(5, len(HOTEL_AMENITIES))), allow_duplicates=False) if HOTEL_AMENITIES else [],
    }


def generate_flight_data(flight_id: str, tour_id: int) -> Dict[str, Any]:
    """Генерирует данные для одного вылета."""
    availability_statuses = ['available', 'limited', 'sold_out']
    
    return {
        'id': flight_id,
        'tour_id': tour_id,
        'price': round(random.uniform(300, 2000), 2),
        'availability_status': random.choice(availability_statuses),
    }


def generate_flight_direction_data(
    direction_id: int,
    flight_id: str,
    direction_type: str,  # 'outbound' или 'inbound'
    departure_date: datetime,
    tour_duration: int
) -> Dict[str, Any]:
    """
    Генерирует данные для одного направления перелета.
    
    Args:
        direction_id: ID направления
        flight_id: UUID вылета
        direction_type: 'outbound' или 'inbound'
        departure_date: Дата вылета (для outbound) или дата возврата (для inbound)
        tour_duration: Продолжительность тура в днях
    """
    return {
        'id': direction_id,
        'flight_id': flight_id,
        'direction': direction_type,
        'inclusions': get_random_items(FLIGHT_INCLUSIONS, random.randint(1, min(4, len(FLIGHT_INCLUSIONS))), allow_duplicates=False) if FLIGHT_INCLUSIONS else [],
        'departure_date': departure_date,
    }


def generate_flight_layover_data(
    layover_id: int,
    flight_direction_id: int,
    direction_type: str,  # 'outbound' или 'inbound'
    node_position: str,  # 'start', 'layover', 'end'
) -> Dict[str, Any]:
    """
    Генерирует данные для одного узла перелета (пересадки или конечной точки).
    
    Args:
        layover_id: ID узла перелета
        flight_direction_id: ID направления перелета
        direction_type: 'outbound' (туда) или 'inbound' (обратно)
        node_position: 'start' (начало), 'layover' (пересадка), 'end' (конец)
    """
    if not RUSSIAN_CITIES or not SAUDI_CITIES or not LAYOVER_CITIES:
        raise ValueError("RUSSIAN_CITIES, SAUDI_CITIES и LAYOVER_CITIES должны быть заполнены.")
    
    # Выбираем город в зависимости от направления и позиции
    if node_position == 'start':
        # Начальная точка: для outbound - российский город, для inbound - саудовский
        if direction_type == 'outbound':
            iata, city = get_random_item(RUSSIAN_CITIES)
        else:  # inbound
            iata, city = get_random_item(SAUDI_CITIES)
        layover_minutes = 0
    elif node_position == 'layover':
        # Пересадка: всегда город из списка пересадок
        iata, city = get_random_item(LAYOVER_CITIES)
        layover_minutes = random.randint(30, 480)  # 30-480 минут для пересадок
    elif node_position == 'end':
        # Конечная точка: для outbound - саудовский город, для inbound - российский
        if direction_type == 'outbound':
            iata, city = get_random_item(SAUDI_CITIES)
        else:  # inbound
            iata, city = get_random_item(RUSSIAN_CITIES)
        layover_minutes = 0
    else:
        raise ValueError(f"Неизвестная позиция узла: {node_position}. Допустимые значения: 'start', 'layover', 'end'")
    
    return {
        'id': layover_id,
        'flight_direction_id': flight_direction_id,
        'iata': iata,
        'city': city,
        'layover_minutes': layover_minutes,
    }


def generate_monthly_flight_dates(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Генерирует даты вылетов: 4-5 вылетов в месяц с декабря 2025 до июля 2026.
    
    Args:
        start_date: Начальная дата (декабрь 2025)
        end_date: Конечная дата (июль 2026)
    
    Returns:
        Список дат вылетов
    """
    flight_dates = []
    current_date = start_date
    
    while current_date <= end_date:
        # Определяем последний день месяца
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)
        last_day_of_month = (next_month - timedelta(days=1)).day
        
        # Генерируем 4-5 вылетов в текущем месяце
        num_flights = random.randint(4, 5)
        days_in_month = list(range(1, last_day_of_month + 1))
        selected_days = random.sample(days_in_month, min(num_flights, len(days_in_month)))
        
        for day in sorted(selected_days):
            flight_date = current_date.replace(day=day)
            # Добавляем случайное время в течение дня
            flight_date = flight_date.replace(
                hour=random.randint(6, 23),
                minute=random.choice([0, 15, 30, 45])
            )
            flight_dates.append(flight_date)
        
        # Переходим к следующему месяцу
        current_date = next_month
    
    return sorted(flight_dates)


def generate_mock_data(
    num_operators: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Генерирует все мок-данные для заполнения базы данных.
    
    Args:
        num_operators: Количество туроператоров
    
    Returns:
        Словарь с данными для всех таблиц
    """
    operators = []
    tours = []
    hotels = []
    flights = []
    flight_directions = []
    flight_layovers = []
    
    # Период генерации вылетов: декабрь 2025 - июль 2026
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2026, 7, 31)
    
    # Генерируем даты вылетов для всех месяцев
    all_flight_dates = generate_monthly_flight_dates(start_date, end_date)
    
    # Счетчики ID
    operator_id = 1
    tour_id = 1
    hotel_id = 1
    flight_direction_id = 1
    layover_id = 1
    
    # Создаем копии списков для удаления использованных элементов
    available_logos = OPERATOR_LOGOS.copy()
    available_names = OPERATOR_NAMES.copy()
    available_descriptions = OPERATOR_DESCRIPTIONS.copy()
    
    # Генерация операторов
    for _ in range(num_operators):
        operator_data, available_logos, available_names, available_descriptions = generate_operator_data(
            operator_id, available_logos, available_names, available_descriptions
        )
        operators.append(operator_data)
        
        # Генерация туров для оператора (3-5 туров)
        num_tours = random.randint(3, 5)
        for _ in range(num_tours):
            tour_data = generate_tour_data(tour_id, operator_id, operator_data)
            tours.append(tour_data)
            tour_duration = tour_data['duration']
            
            # Генерация отелей для тура: всегда 2 отеля (Мекка и Медина)
            hotel_makkah = generate_hotel_data(hotel_id, tour_id, 'Мекка')
            hotels.append(hotel_makkah)
            hotel_id += 1
            
            hotel_madinah = generate_hotel_data(hotel_id, tour_id, 'Медина')
            hotels.append(hotel_madinah)
            hotel_id += 1
            
            # Генерация вылетов для тура: по датам из all_flight_dates
            # Каждый тур использует все доступные даты вылетов
            for outbound_date in all_flight_dates:
                flight_uuid = str(uuid4())
                flight_data = generate_flight_data(flight_uuid, tour_id)
                flights.append(flight_data)
                
                # Дата возврата (inbound) - через duration дней после вылета
                inbound_date = outbound_date + timedelta(days=tour_duration)
                
                # Генерируем количество пересадок для каждого направления (0 или 1)
                outbound_layovers_count = random.choice([0, 1])
                inbound_layovers_count = random.choice([0, 1])
                
                # Генерация outbound направления
                outbound_direction = generate_flight_direction_data(
                    flight_direction_id, flight_uuid, 'outbound', outbound_date, tour_duration
                )
                flight_directions.append(outbound_direction)
                outbound_direction_id = flight_direction_id
                flight_direction_id += 1
                
                # Генерация inbound направления
                inbound_direction = generate_flight_direction_data(
                    flight_direction_id, flight_uuid, 'inbound', inbound_date, tour_duration
                )
                flight_directions.append(inbound_direction)
                inbound_direction_id = flight_direction_id
                flight_direction_id += 1
                
                # Генерация узлов перелета для outbound направления
                # Начальная точка (российский город) + пересадки (0 или 1) + конечная точка (саудовский город)
                num_outbound_nodes = outbound_layovers_count + 2  # +2 для начальной и конечной точек
                for i in range(num_outbound_nodes):
                    if i == 0:
                        node_position = 'start'  # Российский город
                    elif i == num_outbound_nodes - 1:
                        node_position = 'end'  # Саудовский город
                    else:
                        node_position = 'layover'  # Город для пересадки
                    
                    layover_data = generate_flight_layover_data(
                        layover_id, outbound_direction_id, 'outbound', node_position
                    )
                    flight_layovers.append(layover_data)
                    layover_id += 1
                
                # Генерация узлов перелета для inbound направления
                # Начальная точка (саудовский город) + пересадки (0 или 1) + конечная точка (российский город)
                num_inbound_nodes = inbound_layovers_count + 2  # +2 для начальной и конечной точек
                for i in range(num_inbound_nodes):
                    if i == 0:
                        node_position = 'start'  # Саудовский город
                    elif i == num_inbound_nodes - 1:
                        node_position = 'end'  # Российский город
                    else:
                        node_position = 'layover'  # Город для пересадки
                    
                    layover_data = generate_flight_layover_data(
                        layover_id, inbound_direction_id, 'inbound', node_position
                    )
                    flight_layovers.append(layover_data)
                    layover_id += 1
            
            tour_id += 1
        
        operator_id += 1
    
    return {
        'operators': operators,
        'tours': tours,
        'hotels': hotels,
        'flights': flights,
        'flight_directions': flight_directions,
        'flight_layovers': flight_layovers,
    }
