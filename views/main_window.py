"""
Main application window
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from views.dashboard_widget import DashboardWidget
from views.report_widget import ReportsWidget
from views.settings_widget import SettingsWidget
from views.management_widget import ManagementWidget
from controllers import AuthController
from utils import StyleManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayStation Cafe Management System")
        self.setMinimumSize(1200, 800)
        
        self.current_page = None
        
        self.setup_ui()
        self.apply_styles()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def setup_ui(self):
        """Setup UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(15)
        
        # Logo/Title
        logo_label = QLabel("🎮 PlayStation\nCafe Manager")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_font = QFont()
        logo_font.setPointSize(18)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        sidebar_layout.addWidget(logo_label)
        
        sidebar_layout.addSpacing(30)
        
        # Navigation buttons
        self.dashboard_btn = QPushButton("📊 Dashboard")
        self.dashboard_btn.setCheckable(True)
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        sidebar_layout.addWidget(self.dashboard_btn)
        
        self.reports_btn = QPushButton("📈 Reports")
        self.reports_btn.setCheckable(True)
        self.reports_btn.clicked.connect(self.show_reports)
        sidebar_layout.addWidget(self.reports_btn)
        
        self.management_btn = QPushButton("⚙️ Management")
        self.management_btn.setCheckable(True)
        self.management_btn.clicked.connect(self.show_management)
        sidebar_layout.addWidget(self.management_btn)
        
        self.settings_btn = QPushButton("🔧 Settings")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(self.show_settings)
        sidebar_layout.addWidget(self.settings_btn)
        
        sidebar_layout.addStretch()
        
        # User info
        user = AuthController.get_current_user()
        if user:
            user_label = QLabel(f"👤 {user.full_name}")
            user_label.setWordWrap(True)
            sidebar_layout.addWidget(user_label)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setProperty("class", "danger")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Create pages
        self.dashboard_page = DashboardWidget()
        self.reports_page = ReportsWidget()
        self.management_page = ManagementWidget()
        self.settings_page = SettingsWidget()
        self.settings_page.theme_changed.connect(self.apply_styles)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.management_page)
        self.content_stack.addWidget(self.settings_page)
        
        main_layout.addWidget(self.content_stack)
    
    def apply_styles(self):
        """Apply application styles"""
        colors = StyleManager.get_colors()
        
        sidebar_style = f"""
            QWidget#sidebar {{
                background-color: {colors['card_background']};
                border-right: 2px solid {colors['border']};
            }}
            
            QPushButton {{
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
                color: {colors['text']};
            }}
            
            QPushButton:hover {{
                background-color: {colors['background']};
            }}
            
            QPushButton:checked {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            QPushButton[class="danger"] {{
                background-color: {colors['danger']};
                color: white;
            }}
            
            QPushButton[class="danger"]:hover {{
                background-color: #da190b;
            }}
            
            QLabel {{
                color: {colors['text']};
            }}
        """
        
        self.setStyleSheet(StyleManager.get_main_stylesheet() + sidebar_style)
    
    def show_dashboard(self):
        """Show dashboard page"""
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self._update_nav_buttons(self.dashboard_btn)
        self.dashboard_page.load_playstations()
    
    def show_reports(self):
        """Show reports page"""
        self.content_stack.setCurrentWidget(self.reports_page)
        self._update_nav_buttons(self.reports_btn)
    
    def show_management(self):
        """Show management page"""
        self.content_stack.setCurrentWidget(self.management_page)
        self._update_nav_buttons(self.management_btn)
        self.management_page.load_data()
    
    def show_settings(self):
        """Show settings page"""
        self.content_stack.setCurrentWidget(self.settings_page)
        self._update_nav_buttons(self.settings_btn)
    
    def _update_nav_buttons(self, active_btn: QPushButton):
        """Update navigation button states"""
        for btn in [self.dashboard_btn, self.reports_btn, 
                    self.management_btn, self.settings_btn]:
            btn.setChecked(btn == active_btn)
    
    def logout(self):
        """Logout current user"""
        reply = QMessageBox.question(
            self, "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            AuthController.logout()
            self.close()
            
            # Show login dialog again
            from views.login_dialog import LoginDialog
            login_dialog = LoginDialog()
            if login_dialog.exec():
                self.__init__()
                self.show()
    
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()