"""
Build configuration for PlayStation Cafe Manager
"""
from pathlib import Path

# Project root (parent of build folder)
PROJECT_ROOT = Path(__file__).parent.parent

# Application metadata
APP_NAME = "PlayStation Cafe Manager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your Company"
APP_DESCRIPTION = "PlayStation Cafe Management System"
APP_IDENTIFIER = "com.yourcompany.pscafe"

# Paths
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
RESOURCES_DIR = PROJECT_ROOT / "resources"
ICON_FILE = RESOURCES_DIR / "icon.ico"  # You'll need to create this
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

# Build settings
CONSOLE = False  # Set to True for debugging
ONE_FILE = True  # Single executable
UPX = True  # Compress executable

# Files to include
INCLUDE_FILES = [
    (str(RESOURCES_DIR), "resources"),
]

# Hidden imports (modules that PyInstaller might miss)
HIDDEN_IMPORTS = [
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.ext.baked',
    'PyQt6.QtMultimedia',
]

# Modules to exclude (reduce size)
EXCLUDES = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'PyQt6.QtWebEngine',
]