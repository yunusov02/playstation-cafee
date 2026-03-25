"""
Configuration settings for the PlayStation Cafe Management System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "playstation_cafe.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Application Settings
APP_NAME = "PlayStation Cafe Manager"
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