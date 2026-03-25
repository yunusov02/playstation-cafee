"""
User model for admin authentication
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib
import secrets

from database import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    salt = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="admin")
    
    def __init__(self, full_name: str, username: str, password: str):
        self.full_name = full_name
        self.username = username
        self.salt = secrets.token_hex(32)
        self.password_hash = self._hash_password(password, self.salt)
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return self.password_hash == self._hash_password(password, self.salt)
    
    def update_password(self, new_password: str):
        """Update user password"""
        self.salt = secrets.token_hex(32)
        self.password_hash = self._hash_password(new_password, self.salt)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"