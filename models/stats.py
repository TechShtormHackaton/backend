from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class Stats(Base):
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('video_path.id'))
    total_states = Column(Integer, default=0)

    video_frame = relationship('VideoPath', back_populates='stats')


