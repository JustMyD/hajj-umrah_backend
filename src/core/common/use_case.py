from abc import abstractmethod, ABC
from typing import Any

from src.core.common.unit_of_work import UnitOfWork


class UseCase(ABC):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError
