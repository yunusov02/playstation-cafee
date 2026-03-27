from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from sqlalchemy import func, and_

from database import get_db
from models import Session, SessionSegment, Playstation, PaymentType


class ReportController:
    """
    Controller for generating reports
    """
    
    @staticmethod
    def get_daily_report(date: datetime = None) -> Dict[str, Any]:

        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return ReportController._generate_report(start_of_day, end_of_day, "Ежедневный")
    
    @staticmethod
    def get_weekly_report(date: datetime = None) -> Dict[str, Any]:

        if date is None:
            date = datetime.now()
        
        start_of_week = date - timedelta(days=date.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7)
        
        return ReportController._generate_report(start_of_week, end_of_week, "Еженедельный")
    
    @staticmethod
    def get_monthly_report(year: int = None, month: int = None) -> Dict[str, Any]:

        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)
        
        return ReportController._generate_report(start_of_month, end_of_month, "Месячный")
    
    @staticmethod
    def get_custom_report(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return ReportController._generate_report(start_date, end_date, "Пользовательский")
    
    @staticmethod
    def _generate_report(start_date: datetime, end_date: datetime, 
                        report_type: str) -> Dict[str, Any]:

        db = get_db()
        
        # Get all completed sessions in date range
        sessions = db.query(Session).filter(
            and_(
                Session.end_time >= start_date,
                Session.end_time < end_date,
                Session.is_active == False
            )
        ).all()
        
        # Calculate totals
        total_sessions = len(sessions)
        total_revenue = sum(s.total_price for s in sessions)
        total_cash = sum(s.cash_amount for s in sessions)
        total_terminal = sum(s.terminal_amount for s in sessions)
        
        # Calculate total hours
        total_seconds = sum(s.duration_seconds for s in sessions)
        total_hours = total_seconds / 3600
        
        # Revenue per playstation
        ps_revenue = {}
        ps_hours = {}
        ps_sessions = {}
        
        for session in sessions:
            ps_id = session.playstation_id
            ps = db.query(Playstation).filter(Playstation.id == ps_id).first()
            ps_name = ps.name if ps else f"PS {ps_id}"
            
            if ps_name not in ps_revenue:
                ps_revenue[ps_name] = 0
                ps_hours[ps_name] = 0
                ps_sessions[ps_name] = 0
            
            ps_revenue[ps_name] += session.total_price
            ps_hours[ps_name] += session.duration_hours
            ps_sessions[ps_name] += 1
        
        # Find most used playstation
        most_used_ps = None
        most_sessions = 0
        for ps_name, count in ps_sessions.items():
            if count > most_sessions:
                most_sessions = count
                most_used_ps = ps_name
        
        # Calculate joystick usage
        total_joystick_hours = 0
        extra_joystick_revenue = 0
        
        for session in sessions:
            for segment in session.segments:
                segment_hours = segment.duration_hours
                extra_joysticks = segment.extra_joysticks
                total_joystick_hours += segment_hours * segment.joystick_count
                extra_joystick_revenue += segment_hours * extra_joysticks * segment.joystick_hour_price
        
        # Payment breakdown
        cash_sessions = len([s for s in sessions if s.payment_type == PaymentType.CASH])
        terminal_sessions = len([s for s in sessions if s.payment_type == PaymentType.TERMINAL])
        hybrid_sessions = len([s for s in sessions if s.payment_type == PaymentType.HYBRID])
        
        return {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'generated_at': datetime.now(),
            
            # Overview
            'total_sessions': total_sessions,
            'total_revenue': total_revenue,
            'total_hours': total_hours,
            
            # Payment breakdown
            'cash_revenue': total_cash,
            'terminal_revenue': total_terminal,
            'cash_sessions': cash_sessions,
            'terminal_sessions': terminal_sessions,
            'hybrid_sessions': hybrid_sessions,
            
            # Playstation breakdown
            'revenue_per_playstation': ps_revenue,
            'hours_per_playstation': ps_hours,
            'sessions_per_playstation': ps_sessions,
            'most_used_playstation': most_used_ps,
            
            # Joystick stats
            'total_joystick_hours': total_joystick_hours,
            'extra_joystick_revenue': extra_joystick_revenue,
            
            # Averages
            'average_session_duration': total_hours / total_sessions if total_sessions > 0 else 0,
            'average_session_revenue': total_revenue / total_sessions if total_sessions > 0 else 0,
        }
    
    @staticmethod
    def get_session_history(limit: int = 100, offset: int = 0) -> List[Session]:
        db = get_db()
        return db.query(Session).filter(
            Session.is_active == False
        ).order_by(Session.end_time.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def export_report_to_dict(report: Dict[str, Any]) -> Dict[str, Any]:
        export_data = report.copy()
        
        # Convert datetime objects to strings
        for key, value in export_data.items():
            if isinstance(value, datetime):
                export_data[key] = value.isoformat()
        
        return export_data