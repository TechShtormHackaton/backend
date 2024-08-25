from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from database.base import Base
from sqlalchemy.orm import relationship


class FrameVideo(Base):
    __tablename__ = 'frame_video'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('video_path.id'))
    frame_path = Column(String)

    power_state = Column(Integer, default=0)
    throws_state = Column(Integer, default=0)
    safes_state = Column(Integer, default=0)
    description = Column(String)
    is_send = Column(Boolean, default=False)

    video_path = relationship('VideoPath', back_populates='video_frame')