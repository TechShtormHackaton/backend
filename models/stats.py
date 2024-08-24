from sqlalchemy import Column, Integer, String
from database.base import Base


class Stats(Base):
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    power_state = Column(Integer, default=0)
    throws = Column(Integer, default=0)
    empty_state = Column(Integer, default=0)
