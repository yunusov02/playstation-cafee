"""
Configuration settings for the PlayStation Cafe Management System
"""
import os
import sys
from pathlib import Path


def get_app_directory() -> Path:
    """
    Get the correct application directory that persists data.
    Works for both development (.py) and production (.exe)
    """
    
    # Check if running as compiled EXE (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Running as EXE
        # Option 1: Use AppData folder (RECOMMENDED for Windows)
        app_data = os.environ.get('APPDATA')
        if app_data:
            app_dir = Path(app_data) / "PlayStationCafe"
        else:
            # Fallback: Same folder as EXE
            app_dir = Path(sys.executable).parent / "PlayStationCafe_Data"
    else:
        # Running as Python script (development)
        app_dir = Path(__file__).resolve().parent
    
    return app_dir


def get_database_path() -> Path:
    """Get the database file path"""
    app_dir = get_app_directory()
    data_dir = app_dir / "data"
    
    # Create directories if they don't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = data_dir / "playstation_cafe.db"
    
    # Debug: Print the path
    print(f"[CONFIG] App Directory: {app_dir}")
    print(f"[CONFIG] Database Path: {db_path}")
    print(f"[CONFIG] Running as EXE: {getattr(sys, 'frozen', False)}")
    
    return db_path


def get_assets_path() -> Path:
    """Get the assets folder path"""
    if getattr(sys, 'frozen', False):
        # Running as EXE - assets are bundled
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).resolve().parent
    
    return base_path / "assets"


# Base directory
# BASE_DIR = Path(__file__).resolve().parent

BASE_DIR = get_app_directory()
DATABASE_PATH = get_database_path()
ASSETS_PATH = get_assets_path()

# Database
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Application Settings
APP_NAME = "Amir Arena"
APP_VERSION = "1.0.0"

# Default Pricing (in UZS)
DEFAULT_PS_HOUR_PRICE = 10000
DEFAULT_JOYSTICK_HOUR_PRICE = 2500
FREE_JOYSTICKS_PER_SESSION = 2
MAX_JOYSTICKS_PER_SESSION = 5

# Timer Settings
TIMER_UPDATE_INTERVAL = 1000  # milliseconds
WARNING_MINUTES_BEFORE_END = 5

# UI Settings
CARD_WIDTH = 280
CARD_HEIGHT = 320
GRID_SPACING = 20

# Sound Settings
SOUND_ENABLED = True
SOUND_VOLUME = 0.7

