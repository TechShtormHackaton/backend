from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from models.video_path import VideoPath
from models.frame_video import FrameVideo

from database.session import get_session


class LoadFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_video_path(self, data: VideoPath):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def add_frame_path(self, data: FrameVideo):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data


def load_message_repository(session: AsyncSession = Depends(get_session)) -> LoadFileRepository:
    return LoadFileRepository(session)
