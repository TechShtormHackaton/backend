from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from models.video_path import VideoPath
from sqlalchemy.future import select
from database.session import get_session


class LoadFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_video_path(self, data: VideoPath):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def get_video_path(self) -> VideoPath:
        result = await self.session.execute(select(VideoPath))
        return result.scalar()

    async def update_models(self):
        await self.session.commit()

    async def get_video_by_name(self, video_name: str):
        query = select(VideoPath).filter_by(video_name=video_name)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_videos_by_name(self, video_name: str):
        query = select(VideoPath).filter_by(video_name=video_name)
        result = await self.session.execute(query)
        return result.scalars().all()


def load_message_repository(session: AsyncSession = Depends(get_session)) -> LoadFileRepository:
    return LoadFileRepository(session)
