from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import joinedload

from models.video_path import VideoPath
from models.video_frame import FrameVideo
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

    async def add_frame_path(self, data: FrameVideo):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def get_latest_video(self) -> VideoPath:
        result = await self.session.execute(
            select(VideoPath)
            .options(joinedload(VideoPath.video_frame))
            .order_by(VideoPath.id.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def update_frame_path(self, frame_video: FrameVideo):
        """Обновление статуса отправки фрейма."""
        await self.session.execute(
            update(FrameVideo)
            .where(FrameVideo.id == frame_video.id)
            .values(is_send=frame_video.is_send)
        )
        await self.session.commit()

def load_message_repository(session: AsyncSession = Depends(get_session)) -> LoadFileRepository:
    return LoadFileRepository(session)
