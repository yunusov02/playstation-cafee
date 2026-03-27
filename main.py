"""
Main application entry point
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from database import init_db, close_db
from controllers import AuthController
from views import LoginDialog, MainWindow
from utils import StyleManager, SoundManager
from config import APP_NAME


def setup_database():
    """
    Initialize database and create default data
    """
    init_db()
    
    # Ensure admin user exists
    AuthController.ensure_admin_exists()
    
    # Create sample data if needed
    from controllers import PlaystationController, JoystickController
    
    # Check if we need sample data
    if len(PlaystationController.get_all_playstations()) == 0:
        # Create sample playstations
        PlaystationController.create_playstation("PS5 #1", "PS5", 15000)
        PlaystationController.create_playstation("PS5 #2", "PS5", 15000)
        PlaystationController.create_playstation("PS4 #1", "PS4", 10000)
        PlaystationController.create_playstation("PS4 #2", "PS4", 10000)
    
    if len(JoystickController.get_all_joysticks()) == 0:
        # Create sample joysticks (at least 8 for 4 playstations)
        for i in range(1, 13):
            model = "DualSense" if i <= 6 else "DualShock 4"
            JoystickController.create_joystick(f"Joystick #{i}", model, 2500)


def main():
    """
    Main application entry point
    """
    
    # Enable high DPI scalings
    # DPI - Dots Per Inch scalings -> How many pixels fit in one inch of your screen
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Initialize systems
    setup_database()
    SoundManager.initialize()
    
    # Show login dialog
    login_dialog = LoginDialog()
    
    if login_dialog.exec():
        # Login successful, show main window
        main_window = MainWindow()
        main_window.show()
        
        exit_code = app.exec()
        
        # Cleanup
        close_db()
        
        sys.exit(exit_code)
    else:
        # Login cancelled
        close_db()
        sys.exit(0)


if __name__ == "__main__":
    main()