from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID

from src.core.tours.read_models.get_tarifs_read_model import TourTarifReadModel
from src.core.tours.read_models.tour_search_read_model import TourSearchReadModel
from src.core.tours.read_models.tours_aggregates_read_model import ToursAggregatesReadModel
from src.core.tours.read_models.tours_departure_cities_read_model import ToursDepartureCitiesReadModel


class TourRepository(ABC):
    """
    Порт: интерфейс для репозитория туров.
    Реализация предоставляется в infrastructure/db/repositories/...
    """

    @abstractmethod
    async def search(
        self,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
        departure_city: Optional[str],
        departure_date_mode: Literal["single", "range"],
        departure_date: Optional[datetime],
        departure_date_start: Optional[datetime],
        departure_date_end: Optional[datetime],
        pilgrims: Optional[int],
        limit: int = 20,
        offset: int = 0,
    ) -> List[TourSearchReadModel]:
        """
        Получение списка туров по фильтрам
        :param tour_type:            Тип тура
        :param tarif:                Тариф
        :param operator_id:          Id туроператора
        :param departure_city:       Город отправления
        :param departure_date_mode:  Тип поиска даты вылета (`single` or `range`)
        :param departure_date:       Дата вылета (для `single`)
        :param departure_date_start: Начало диапазона даты вылета (для `range`)
        :param departure_date_end:   Конец диапазона даты вылета (для `single`)
        :param pilgrims:             Количество путешественников
        :param limit:                Кол-во записей
        :param offset:               Смещение
        :return:                     Детальный список туров
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, tour_ids: List[UUID]) -> List[TourSearchReadModel]:
        """
        Получение списка туров по id
        :param tour_ids: Список ID туров
        :return:         Детальный список туров
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tours_aggregates(
        self,
        from_date: datetime,
        to_date: datetime,
        tour_type: Optional[str],
        tarif: Optional[str],
        operator_id: Optional[int],
    ) -> List[ToursAggregatesReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_tour_tarifs(self) -> List[TourTarifReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_tours_departure_cities(self) -> List[ToursDepartureCitiesReadModel]:
        raise NotImplementedError
