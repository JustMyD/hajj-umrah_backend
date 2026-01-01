from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.operator.read_models.operator_search_read_model import OperatorSearchReadModel
from src.core.operator.ports.operator_repository import OperatorRepository
from src.infrastructure.db.models.operator import Operators


class SqlAlchemyOperatorRepository(OperatorRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, limit: int = 20, offset: int = 0) -> List[OperatorSearchReadModel]:
        stmt = select(Operators)
        result = await self.session.execute(stmt)
        models = result.scalars().unique().all()

        return [
            OperatorSearchReadModel(
                id=m.id,
                name=m.name,
                description=m.description,
                logo=m.logo,
                foundation_year=m.foundation_year,
                rating=m.rating,
                reviews_count=m.reviews_count,
                specialisations=m.specialisations,
                features=m.features,
                certificates=m.certificates,
                verified=m.verified
            ) for m in models
        ]
