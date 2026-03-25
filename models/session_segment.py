"""
Session Segment model for tracking joystick changes during session
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base
from config import FREE_JOYSTICKS_PER_SESSION


class SessionSegment(Base):
    __tablename__ = 'session_segments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    
    joystick_count = Column(Integer, default=2)
    ps_hour_price = Column(Float, nullable=False)
    joystick_hour_price = Column(Float, nullable=False)
    
    segment_price = Column(Float, default=0.0)
    
    # Relationship
    session = relationship("Session", back_populates="segments")
    
    def __init__(self, session_id: int, joystick_count: int,
                 ps_hour_price: float, joystick_hour_price: float):
        self.session_id = session_id
        self.joystick_count = joystick_count
        self.ps_hour_price = ps_hour_price
        self.joystick_hour_price = joystick_hour_price
        self.start_time = datetime.now()
    
    @property
    def duration_seconds(self) -> float:
        """Get segment duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def duration_hours(self) -> float:
        """Get segment duration in hours"""
        return self.duration_seconds / 3600
    
    @property
    def extra_joysticks(self) -> int:
        """Get number of extra (paid) joysticks"""
        return max(0, self.joystick_count - FREE_JOYSTICKS_PER_SESSION)
    
    def calculate_price(self) -> float:
        """
        Calculate segment price
        Formula: duration_hours * ps_price + duration_hours * extra_joysticks * joystick_price
        """
        hours = self.duration_hours
        ps_cost = hours * self.ps_hour_price
        joystick_cost = hours * self.extra_joysticks * self.joystick_hour_price
        
        self.segment_price = ps_cost + joystick_cost
        return self.segment_price
    
    def close(self):
        """Close the segment"""
        self.end_time = datetime.now()
        self.calculate_price()
    
    def __repr__(self):
        return f"<SessionSegment(id={self.id}, session_id={self.session_id}, joysticks={self.joystick_count})>"