from sqlalchemy import Column, Integer, String, ForeignKey
from database.base import Base
from sqlalchemy.orm import relationship


class FrameVideo(Base):
    __tablename__ = 'frame_video'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('video_path.id'))
    frame_path = Column(String)

    video_path = relationship('VideoPath', back_populates='video_frame')
