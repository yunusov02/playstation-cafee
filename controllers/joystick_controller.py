"""
Joystick management controller
"""
from typing import List, Tuple, Optional

from database import get_db
from models import Joystick, JoystickStatus
from config import DEFAULT_JOYSTICK_HOUR_PRICE


class JoystickController:
    """Controller for Joystick management"""
    
    @staticmethod
    def create_joystick(name: str, model: str,
                       price_per_hour: float = DEFAULT_JOYSTICK_HOUR_PRICE) -> Tuple[bool, str]:
        """Create new joystick"""
        db = get_db()
        try:
            joystick = Joystick(name=name, model=model, price_per_hour=price_per_hour)
            db.add(joystick)
            db.commit()
            
            return True, f"Joystick '{name}' created successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating joystick: {str(e)}"
    
    @staticmethod
    def get_all_joysticks() -> List[Joystick]:
        """Get all active joysticks"""
        db = get_db()
        return db.query(Joystick).filter(Joystick.is_active == True).all()
    
    @staticmethod
    def get_available_joysticks() -> List[Joystick]:
        """Get all available joysticks"""
        db = get_db()
        return db.query(Joystick).filter(
            Joystick.status == JoystickStatus.AVAILABLE,
            Joystick.is_active == True
        ).all()
    
    @staticmethod
    def get_available_count() -> int:
        """Get count of available joysticks"""
        db = get_db()
        return db.query(Joystick).filter(
            Joystick.status == JoystickStatus.AVAILABLE,
            Joystick.is_active == True
        ).count()
    
    @staticmethod
    def get_total_count() -> int:
        """Get total count of active joysticks"""
        db = get_db()
        return db.query(Joystick).filter(Joystick.is_active == True).count()
    
    @staticmethod
    def allocate_joysticks(count: int) -> Tuple[bool, str]:
        """Allocate joysticks for a session"""
        db = get_db()
        try:
            available = db.query(Joystick).filter(
                Joystick.status == JoystickStatus.AVAILABLE,
                Joystick.is_active == True
            ).limit(count).all()
            
            if len(available) < count:
                return False, f"Not enough joysticks. Available: {len(available)}, Requested: {count}"
            
            for joystick in available:
                joystick.status = JoystickStatus.IN_USE
            
            db.commit()
            return True, "Joysticks allocated"
            
        except Exception as e:
            db.rollback()
            return False, f"Error allocating joysticks: {str(e)}"
    
    @staticmethod
    def release_joysticks(count: int) -> Tuple[bool, str]:
        """Release joysticks back to pool"""
        db = get_db()
        try:
            in_use = db.query(Joystick).filter(
                Joystick.status == JoystickStatus.IN_USE,
                Joystick.is_active == True
            ).limit(count).all()
            
            for joystick in in_use:
                joystick.status = JoystickStatus.AVAILABLE
            
            db.commit()
            return True, "Joysticks released"
            
        except Exception as e:
            db.rollback()
            return False, f"Error releasing joysticks: {str(e)}"
    
    @staticmethod
    def update_joystick(joystick_id: int, name: str = None, model: str = None,
                       price_per_hour: float = None) -> Tuple[bool, str]:
        """Update joystick details"""
        db = get_db()
        try:
            joystick = db.query(Joystick).filter(Joystick.id == joystick_id).first()
            if not joystick:
                return False, "Joystick not found"
            
            if name:
                joystick.name = name
            if model:
                joystick.model = model
            if price_per_hour is not None:
                joystick.price_per_hour = price_per_hour
            
            db.commit()
            return True, "Joystick updated successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating joystick: {str(e)}"
    
    @staticmethod
    def delete_joystick(joystick_id: int) -> Tuple[bool, str]:
        """Deactivate joystick"""
        db = get_db()
        try:
            joystick = db.query(Joystick).filter(Joystick.id == joystick_id).first()
            if not joystick:
                return False, "Joystick not found"
            
            if joystick.status == JoystickStatus.IN_USE:
                return False, "Cannot delete joystick in use"
            
            joystick.is_active = False
            db.commit()
            return True, "Joystick deleted"
            
        except Exception as e:
            db.rollback()
            return False, f"Error deleting joystick: {str(e)}"
    
    @staticmethod
    def get_default_price() -> float:
        """Get default joystick price"""
        db = get_db()
        joystick = db.query(Joystick).filter(Joystick.is_active == True).first()
        if joystick:
            return joystick.price_per_hour
        return DEFAULT_JOYSTICK_HOUR_PRICE