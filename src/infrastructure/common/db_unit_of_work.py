from sqlalchemy.ext.asyncio import AsyncSession

from src.core.common.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
