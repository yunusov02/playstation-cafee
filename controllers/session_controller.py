from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict

from database import get_db
from models import (
    Session, SessionSegment, SessionType, PaymentType,
    Playstation, PlaystationStatus
)
from .joystick_controller import JoystickController
from .playstation_controller import PlaystationController
from config import FREE_JOYSTICKS_PER_SESSION, MAX_JOYSTICKS_PER_SESSION


class SessionController:
    """
    Controller for Session management
    """
    
    @staticmethod
    def start_session(
        playstation_id: int, 
        admin_id: int, 
        session_type: SessionType,
        target_value: Optional[float] = None,
        initial_joysticks: int = 2
    ) -> Tuple[bool, str, Optional[Session]]:
        """
        Start a new session
        
        Args:
            playstation_id: ID of the playstation
            admin_id: ID of the admin starting the session
            session_type: Type of session (HOURLY, AMOUNT, VIP)
            target_value: Target hours or amount (None for VIP)
            initial_joysticks: Initial number of joysticks (default 2, free)
        
        Returns:
            Tuple of (success, message, session_object)
        """
        db = get_db()
        try:
            # Get playstation
            ps = db.query(Playstation).filter(Playstation.id == playstation_id).first()
            if not ps:
                return False, "Playstation не найден", None
            
            if ps.status != PlaystationStatus.FREE:
                return False, "Playstation не доступен", None
            
            # Check joystick availability
            if initial_joysticks > FREE_JOYSTICKS_PER_SESSION:
                extra_needed = initial_joysticks - FREE_JOYSTICKS_PER_SESSION
                available = JoystickController.get_available_count()
                if available < extra_needed:
                    return False, f"Нет в наличии. Доступно: {available}", None
            
            # Create session
            session = Session(
                playstation_id=playstation_id,
                admin_id=admin_id,
                session_type=session_type,
                target_value=target_value
            )
            db.add(session)
            db.flush()  # Get session ID
            
            # Create first segment
            joystick_price = JoystickController.get_default_price()
            segment = SessionSegment(
                session_id=session.id,
                joystick_count=initial_joysticks,
                ps_hour_price=ps.price_per_hour,
                joystick_hour_price=joystick_price
            )
            db.add(segment)
            
            # Update playstation status
            ps.status = PlaystationStatus.RUNNING
            
            # Allocate extra joysticks if needed
            if initial_joysticks > FREE_JOYSTICKS_PER_SESSION:
                JoystickController.allocate_joysticks(
                    initial_joysticks - FREE_JOYSTICKS_PER_SESSION
                )
            
            db.commit()
            db.refresh(session)
            
            return True, "Сессия успешно запущена", session
            
        except Exception as e:
            db.rollback()
            return False, f"Error starting session: {str(e)}", None
    
    @staticmethod
    def modify_session_joysticks(session_id: int, new_joystick_count: int) -> Tuple[bool, str]:
        """
        Modify joystick count during session
        
        This closes the current segment and creates a new one with updated joystick count
        """
        db = get_db()
        try:
            session = db.query(Session).filter(
                Session.id == session_id,
                Session.is_active == True
            ).first()
            
            if not session:
                return False, "Активная сессия не найдена"
            
            # Validate joystick count
            if new_joystick_count < FREE_JOYSTICKS_PER_SESSION:
                return False, f"Минимальное количество джойстиков: {FREE_JOYSTICKS_PER_SESSION}"
            
            if new_joystick_count > MAX_JOYSTICKS_PER_SESSION:
                return False, f"Максимальное количество джойстиков: {MAX_JOYSTICKS_PER_SESSION}"
            
            current_count = session.current_joystick_count
            
            if new_joystick_count == current_count:
                return True, "Количество джойстиков не изменилось"
            
            # Check joystick availability if adding
            if new_joystick_count > current_count:
                extra_needed = new_joystick_count - current_count
                available = JoystickController.get_available_count()
                if available < extra_needed:
                    return False, f"Нет в наличии. Доступно: {available}"
            
            # Close current segment
            current_segment = next(
                (s for s in session.segments if s.end_time is None),
                None
            )
            
            if current_segment:
                current_segment.close()
            
            # Get playstation price
            ps = db.query(Playstation).filter(
                Playstation.id == session.playstation_id
            ).first()
            
            # Create new segment
            new_segment = SessionSegment(
                session_id=session.id,
                joystick_count=new_joystick_count,
                ps_hour_price=ps.price_per_hour,
                joystick_hour_price=JoystickController.get_default_price()
            )
            db.add(new_segment)
            
            # Update joystick allocation
            if new_joystick_count > current_count:
                # Need more joysticks
                extra = new_joystick_count - current_count
                JoystickController.allocate_joysticks(extra)
            else:
                # Release some joysticks
                release_count = current_count - new_joystick_count
                JoystickController.release_joysticks(release_count)
            
            db.commit()
            return True, f"Количество джойстиков обновлено до {new_joystick_count}"
            
        except Exception as e:
            db.rollback()
            return False, f"Error modifying session: {str(e)}"
    
    @staticmethod
    def end_session(session_id: int, payment_type: PaymentType,
                   cash_amount: float = 0, terminal_amount: float = 0,
                   notes: str = None) -> Tuple[bool, str, float]:
        """
        End a session
        
        Returns:
            Tuple of (success, message, total_price)
        """
        db = get_db()
        try:
            session = db.query(Session).filter(
                Session.id == session_id,
                Session.is_active == True
            ).first()
            
            if not session:
                return False, "Active session not found", 0
            
            # Close active segment
            for segment in session.segments:
                if segment.end_time is None:
                    segment.close()
            
            # Calculate total price
            total_price = session.calculate_total_price()
            
            # Validate payment
            if payment_type == PaymentType.CASH:
                cash_amount = total_price
                terminal_amount = 0
            elif payment_type == PaymentType.TERMINAL:
                cash_amount = 0
                terminal_amount = total_price
            elif payment_type == PaymentType.HYBRID:
                if abs((cash_amount + terminal_amount) - total_price) > 500:  # Allow 1 UZS tolerance
                    return False, "Наличные + Терминал должны равняться общей цене +-500", total_price
            
            # End session
            session.end_session(
                payment_type=payment_type,
                cash_amount=cash_amount,
                terminal_amount=terminal_amount
            )
            session.notes = notes
            
            # Update playstation status
            ps = db.query(Playstation).filter(
                Playstation.id == session.playstation_id
            ).first()
            ps.status = PlaystationStatus.FREE
            
            # Release all joysticks
            joystick_count = session.current_joystick_count
            if joystick_count > FREE_JOYSTICKS_PER_SESSION:
                JoystickController.release_joysticks(
                    joystick_count - FREE_JOYSTICKS_PER_SESSION
                )
            
            db.commit()
            return True, "Сессия завершена", total_price
            
        except Exception as e:
            db.rollback()
            return False, f"Error ending session: {str(e)}", 0
    
    @staticmethod
    def get_active_session(playstation_id: int) -> Optional[Session]:
        """Get active session for a playstation"""
        db = get_db()
        return db.query(Session).filter(
            Session.playstation_id == playstation_id,
            Session.is_active == True
        ).first()
    
    @staticmethod
    def get_all_active_sessions() -> List[Session]:
        """Get all active sessions"""
        db = get_db()
        return db.query(Session).filter(Session.is_active == True).all()
    
    @staticmethod
    def calculate_current_price(session: Session) -> float:
        """Calculate current price for an active session"""
        total = 0
        for segment in session.segments:
            total += segment.calculate_price()
        return total
    
    @staticmethod
    def get_session_info(session: Session) -> Dict:
        """Get detailed session information"""
        now = datetime.now()
        elapsed = (now - session.start_time).total_seconds()
        
        # Calculate remaining time based on session type
        remaining_seconds = None
        remaining_amount = None
        
        if session.session_type == SessionType.HOURLY:
            target_seconds = session.target_value * 3600
            remaining_seconds = target_seconds - elapsed
            
        elif session.session_type == SessionType.AMOUNT:
            current_price = SessionController.calculate_current_price(session)
            remaining_amount = session.target_value - current_price
            # Estimate remaining time based on current rate
            if elapsed > 0:
                rate_per_second = current_price / elapsed
                if rate_per_second > 0:
                    remaining_seconds = remaining_amount / rate_per_second
        
        return {
            'session_id': session.id,
            'playstation_id': session.playstation_id,
            'session_type': session.session_type,
            'start_time': session.start_time,
            'elapsed_seconds': elapsed,
            'remaining_seconds': remaining_seconds,
            'remaining_amount': remaining_amount,
            'current_price': SessionController.calculate_current_price(session),
            'joystick_count': session.current_joystick_count,
            'target_value': session.target_value,
            'is_overdue': remaining_seconds is not None and remaining_seconds < 0
        }
    
    @staticmethod
    def check_overdue_sessions():
        """Check and update overdue sessions"""
        db = get_db()
        active_sessions = db.query(Session).filter(Session.is_active == True).all()
        
        for session in active_sessions:
            info = SessionController.get_session_info(session)
            ps = db.query(Playstation).filter(
                Playstation.id == session.playstation_id
            ).first()
            
            if info['is_overdue']:
                ps.status = PlaystationStatus.OVERDUE
            else:
                ps.status = PlaystationStatus.RUNNING
        
        db.commit()

