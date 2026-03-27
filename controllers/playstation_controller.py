from typing import List, Optional, Tuple

from database import get_db
from models import Playstation, PlaystationStatus
from config import DEFAULT_PS_HOUR_PRICE


class PlaystationController:
    """
    Controller for Playstation management
    """
    
    @staticmethod
    def create_playstation(
        name: str, 
        model: str, 
        price_per_hour: float = DEFAULT_PS_HOUR_PRICE
    ) -> Tuple[bool, str]:
        
        db = get_db()
        try:
            # Check if name exists
            existing = db.query(Playstation).filter(Playstation.name == name).first()
            if existing:
                return False, "Playstation уже существует"
            
            ps = Playstation(name=name, model=model, price_per_hour=price_per_hour)
            db.add(ps)
            db.commit()
            
            return True, f"Playstation '{name}' создан успешно"
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating playstation: {str(e)}"
    
    @staticmethod
    def get_all_playstations() -> List[Playstation]:

        db = get_db()
        return db.query(Playstation).order_by(Playstation.name).all()
    
    @staticmethod
    def get_playstation(ps_id: int) -> Optional[Playstation]:

        db = get_db()
        return db.query(Playstation).filter(Playstation.id == ps_id).first()
    
    @staticmethod
    def get_free_playstations() -> List[Playstation]:

        db = get_db()
        return db.query(Playstation).filter(
            Playstation.status == PlaystationStatus.FREE
        ).all()
    
    @staticmethod
    def update_playstation(
        ps_id: int, 
        name: str = None, 
        model: str = None,
        price_per_hour: float = None
    ) -> Tuple[bool, str]:
    
        db = get_db()
        try:
            ps = db.query(Playstation).filter(Playstation.id == ps_id).first()
            if not ps:
                return False, "Playstation не найден"
            
            if name:
                # Check if new name conflicts
                existing = db.query(Playstation).filter(
                    Playstation.name == name,
                    Playstation.id != ps_id
                ).first()
                if existing:
                    return False, "Playstation уже существует"
                ps.name = name
                
            if model:
                ps.model = model
            if price_per_hour is not None:
                ps.price_per_hour = price_per_hour
            
            db.commit()
            return True, "Playstation обновлен успешно"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating playstation: {str(e)}"
    
    @staticmethod
    def delete_playstation(ps_id: int) -> Tuple[bool, str]:

        db = get_db()
        try:
            ps = db.query(Playstation).filter(Playstation.id == ps_id).first()
            if not ps:
                return False, "Playstation не найден"
            
            if ps.status != PlaystationStatus.FREE:
                return False, "Невозможно удалить занятый Playstation"
            
            db.delete(ps)
            db.commit()
            return True, "Playstation удален"
            
        except Exception as e:
            db.rollback()
            return False, f"Error deleting playstation: {str(e)}"
    
    @staticmethod
    def update_status(ps_id: int, status: PlaystationStatus):
        db = get_db()
        try:
            ps = db.query(Playstation).filter(Playstation.id == ps_id).first()
            if ps:
                ps.status = status
                db.commit()
        except Exception:
            db.rollback()