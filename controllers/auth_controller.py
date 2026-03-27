from datetime import datetime
from typing import Optional, Tuple, List

from database import get_db
from models import User


class AuthController:
    """
    Controller for user authentication and management
    """
    
    _current_user: Optional[User] = None
    
    @classmethod
    def login(cls, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user
        Returns: (success, message)
        """
        db = get_db()
        try:
            user = db.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()
            
            if not user:
                return False, "User not found"
            
            if not user.verify_password(password):
                return False, "Invalid password"
            
            user.last_login = datetime.now()
            db.commit()
            
            cls._current_user = user
            return True, "Login successful"
            
        except Exception as e:
            db.rollback()
            return False, f"Login error: {str(e)}"
    
    @classmethod
    def logout(cls):
        """
        Logout current user
        """
        cls._current_user = None
    
    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """
        Get currently logged in user
        """
        return cls._current_user
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """
        Check if user is authenticated
        """
        return cls._current_user is not None
    
    @classmethod
    def create_user(cls, full_name: str, username: str, password: str) -> Tuple[bool, str]:
        
        db = get_db()
        
        try:
            # Check if username exists
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                return False, "Такой пользователь уже существует"
            
            user = User(full_name=full_name, username=username, password=password)
            db.add(user)
            db.commit()
            
            return True, "Пользователь создано успешно"
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating user: {str(e)}"
    
    @classmethod
    def get_all_users(cls) -> List[User]:
        """Get all users"""
        db = get_db()
        return db.query(User).filter(User.is_active == True).all()
    
    @classmethod
    def update_user(
        cls, 
        user_id: int, 
        full_name: str = None, 
        password: str = None
    ) -> Tuple[bool, str]:
    
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Пользователь не найден"
            
            if full_name:
                user.full_name = full_name
            if password:
                user.update_password(password)
            
            db.commit()
            return True, "Пользователь обновлен успешно"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating user: {str(e)}"
    
    @classmethod
    def deactivate_user(cls, user_id: int) -> Tuple[bool, str]:
        
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Пользователь не найден"
            
            user.is_active = False
            db.commit()
            return True, "Пользователь деактивирован успешно"
            
        except Exception as e:
            db.rollback()
            return False, f"Error deactivating user: {str(e)}"
    
    @classmethod
    def ensure_admin_exists(cls):
        """
        Ensure at least one admin user exists
        """
        
        db = get_db()
        admin_count = db.query(User).filter(User.is_active == True).count()
        
        if admin_count == 0:
            cls.create_user("Administrator", "admin", "admin123")

