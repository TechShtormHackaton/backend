from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_session
from fastapi import Depends
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from models.frame_video import FrameVideo
from models.video_path import VideoPath


class WebSocketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_path(self):
        result = await self.session.execute(
            select(VideoPath)
            .options(joinedload(VideoPath.video_frame))
            .order_by(desc(VideoPath.id)))
        return result.scalar()


def get_ws_repository(session: AsyncSession = Depends(get_session)) -> WebSocketRepository:
    return WebSocketRepository(session)
