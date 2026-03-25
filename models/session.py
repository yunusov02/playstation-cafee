"""
Session model for tracking gameplay sessions
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, String
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean

from database import Base


class SessionType(Enum):
    HOURLY = "hourly"       # Fixed hours (1, 1.5, 2, etc.)
    AMOUNT = "amount"       # Fixed amount (15000, 25000, etc.)
    VIP = "vip"             # Play until they want to stop


class PaymentType(Enum):
    CASH = "cash"
    TERMINAL = "terminal"
    HYBRID = "hybrid"


class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    playstation_id = Column(Integer, ForeignKey('playstations.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    session_type = Column(SQLEnum(SessionType), nullable=False)
    
    # For hourly sessions: target hours
    # For amount sessions: target amount
    # For VIP: null
    target_value = Column(Float, nullable=True)
    
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    
    # Pricing
    cash_amount = Column(Float, default=0.0)
    terminal_amount = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    
    payment_type = Column(SQLEnum(PaymentType), nullable=True)
    
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)
    
    # Relationships
    playstation = relationship("Playstation", back_populates="sessions")
    admin = relationship("User", back_populates="sessions")
    segments = relationship("SessionSegment", back_populates="session", 
                          cascade="all, delete-orphan", order_by="SessionSegment.start_time")
    
    def __init__(self, playstation_id: int, admin_id: int, session_type: SessionType,
                 target_value: Optional[float] = None):
        self.playstation_id = playstation_id
        self.admin_id = admin_id
        self.session_type = session_type
        self.target_value = target_value
        self.start_time = datetime.now()
        self.is_active = True
    
    @property
    def duration_seconds(self) -> float:
        """Get total session duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def duration_hours(self) -> float:
        """Get total session duration in hours"""
        return self.duration_seconds / 3600
    
    @property
    def current_joystick_count(self) -> int:
        """Get current joystick count from active segment"""
        if self.segments:
            active_segment = next(
                (s for s in self.segments if s.end_time is None),
                self.segments[-1]
            )
            return active_segment.joystick_count
        return 2
    
    def calculate_total_price(self) -> float:
        """Calculate total price from all segments"""
        total = sum(segment.calculate_price() for segment in self.segments)
        self.total_price = total
        return total
    
    def end_session(self, payment_type: PaymentType, cash_amount: float = 0, 
                    terminal_amount: float = 0):
        """End the session"""
        self.end_time = datetime.now()
        self.is_active = False
        self.payment_type = payment_type
        self.cash_amount = cash_amount
        self.terminal_amount = terminal_amount
        self.calculate_total_price()
        
        # Close any active segments
        for segment in self.segments:
            if segment.end_time is None:
                segment.end_time = self.end_time
    
    def __repr__(self):
        return f"<Session(id={self.id}, ps_id={self.playstation_id}, active={self.is_active})>"

