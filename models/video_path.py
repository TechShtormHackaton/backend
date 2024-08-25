from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class VideoPath(Base):
    __tablename__ = 'video_path'

    id = Column(Integer, primary_key=True)
    path = Column(String)

    power_total = Column(Integer, default=None, nullable=True)
    throws_total = Column(Integer, default=None, nullable=True)
    safes_total = Column(Integer, default=None, nullable=True)

    video_frame = relationship('FrameVideo', back_populates='video_path')
