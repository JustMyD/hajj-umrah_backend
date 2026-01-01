from src.core.operator.ports.operator_repository import OperatorRepository


class SearchOperatorsUseCase:
    def __init__(self, operator_repo: OperatorRepository):
        self.repo = operator_repo

    async def execute(self, limit: int = 20, offset: int = 0):
        if limit <= 0 or offset < 0:
            raise ValueError("invalid pagination")

        return await self.repo.search(limit=limit, offset=offset)