from datetime import datetime, timedelta


def format_time(seconds: float) -> str:
    """
    Format seconds to HH:MM:SS
    """
    if seconds < 0:
        prefix = "-"
        seconds = abs(seconds)
    else:
        prefix = ""
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{prefix}{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration(hours: float) -> str:
    """
    Format hours to readable string
    """
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} min"
    elif hours == int(hours):
        return f"{int(hours)} hr"
    else:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h {m}m"


def format_currency(amount: float, currency: str = "UZS") -> str:
    """
    Format amount to currency string
    """
    return f"{amount:,.0f} {currency}"


def parse_hours(hours_str: str) -> float:
    """
    Parse hours string (e.g., '1.5', '2', '1h30m')
    """
    hours_str = hours_str.strip().lower()
    
    # Check for hour:minute format
    if 'h' in hours_str and 'm' in hours_str:
        parts = hours_str.replace('h', ' ').replace('m', '').split()
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
    
    # Check for simple hour format
    if 'h' in hours_str:
        return float(hours_str.replace('h', ''))
    
    # Assume decimal hours
    return float(hours_str)


def get_time_remaining_color(seconds: float) -> str:
    """
    Get color based on remaining time
    """
    if seconds < 0:
        return 'danger'  # Overdue
    elif seconds < 300:  # Less than 5 minutes
        return 'warning'
    else:
        return 'success'


def calculate_end_time(start_time: datetime, hours: float) -> datetime:
    """
    Calculate end time based on start time and hours
    """
    return start_time + timedelta(hours=hours)


def seconds_until(target_time: datetime) -> float:
    """
    Get seconds until target time
    """
    return (target_time - datetime.now()).total_seconds()