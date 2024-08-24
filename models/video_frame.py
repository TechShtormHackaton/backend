from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class VideoFrame(Base):
    __tablename__ = 'video_frame'

    id = Column(Integer, primary_key=True)
    video_path = Column(String, nullable=False)

    power_state = Column(Integer, default=0)
    throws = Column(Integer, default=0)
    empty_state = Column(Integer, default=0)
