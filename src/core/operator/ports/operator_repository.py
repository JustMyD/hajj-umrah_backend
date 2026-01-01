from abc import ABC, abstractmethod
from typing import List

from src.core.operator.read_models.operator_search_read_model import OperatorSearchReadModel


class OperatorRepository(ABC):
    @abstractmethod
    async def search(self, limit: int = 20, offset: int = 0) -> List[OperatorSearchReadModel]:
        """
        Порт: интерфейс для репозитория операторов.
        Реализация предоставляется в infrastructure/db/repositories/...
        """
        raise NotImplementedError
