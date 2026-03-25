"""
Playstation model
"""
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from database import Base
from config import DEFAULT_PS_HOUR_PRICE


class PlaystationStatus(Enum):
    FREE = "free"
    RUNNING = "running"
    OVERDUE = "overdue"


class Playstation(Base):
    __tablename__ = 'playstations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    model = Column(String(50), nullable=False)  # PS4, PS5, etc.
    price_per_hour = Column(Float, default=DEFAULT_PS_HOUR_PRICE)
    status = Column(SQLEnum(PlaystationStatus), default=PlaystationStatus.FREE)
    
    # Relationships
    sessions = relationship("Session", back_populates="playstation")
    
    def __init__(self, name: str, model: str, price_per_hour: float = DEFAULT_PS_HOUR_PRICE):
        self.name = name
        self.model = model
        self.price_per_hour = price_per_hour
        self.status = PlaystationStatus.FREE
    
    def set_running(self):
        """Set playstation status to running"""
        self.status = PlaystationStatus.RUNNING
    
    def set_free(self):
        """Set playstation status to free"""
        self.status = PlaystationStatus.FREE
    
    def set_overdue(self):
        """Set playstation status to overdue"""
        self.status = PlaystationStatus.OVERDUE
    
    def __repr__(self):
        return f"<Playstation(id={self.id}, name='{self.name}', status={self.status.value})>"