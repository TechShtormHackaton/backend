from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from database.session import get_session


class LoadFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


def load_message_repository(session: AsyncSession = Depends(get_session)) -> LoadFileRepository:
    return LoadFileRepository(session)
