from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class VideoPath(Base):
    __tablename__ = 'video_path'

    id = Column(Integer, primary_key=True)
    path = Column(String)

    power_state = Column(Integer, default=0)
    throws = Column(Integer, default=0)
    empty_state = Column(Integer, default=0)

