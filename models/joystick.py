"""
Joystick model for tracking available controllers
"""
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, Boolean
from enum import Enum

from database import Base
from config import DEFAULT_JOYSTICK_HOUR_PRICE


class JoystickStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"


class Joystick(Base):
    __tablename__ = 'joysticks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)  # DualShock 4, DualSense, etc.
    price_per_hour = Column(Float, default=DEFAULT_JOYSTICK_HOUR_PRICE)
    status = Column(SQLEnum(JoystickStatus), default=JoystickStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    
    def __init__(self, name: str, model: str, price_per_hour: float = DEFAULT_JOYSTICK_HOUR_PRICE):
        self.name = name
        self.model = model
        self.price_per_hour = price_per_hour
        self.status = JoystickStatus.AVAILABLE
    
    def set_in_use(self):
        """Mark joystick as in use"""
        self.status = JoystickStatus.IN_USE
    
    def set_available(self):
        """Mark joystick as available"""
        self.status = JoystickStatus.AVAILABLE
    
    def __repr__(self):
        return f"<Joystick(id={self.id}, name='{self.name}', status={self.status.value})>"