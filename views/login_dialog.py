"""
Login dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controllers import AuthController
from utils import StyleManager


class LoginDialog(QDialog):
    """Login dialog for admin authentication"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - PlayStation Cafe Manager")
        self.setFixedSize(400, 350)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("🎮 PlayStation Cafe")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Admin Login")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(45)
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #F44336; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Exit")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
    
    def apply_styles(self):
        """Apply styles"""
        colors = StyleManager.get_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['card_background']};
                border-radius: 15px;
            }}
            
            QLabel#title {{
                color: {colors['primary']};
            }}
            
            QLineEdit {{
                padding: 12px 15px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            
            QLineEdit:focus {{
                border-color: {colors['primary']};
            }}
            
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            
            QPushButton[class="secondary"] {{
                background-color: transparent;
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
            }}
            
            QPushButton[class="secondary"]:hover {{
                background-color: {colors['background']};
            }}
        """)
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Please enter username and password")
            return
        
        success, message = AuthController.login(username, password)
        
        if success:
            self.accept()
        else:
            self.error_label.setText(message)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def mousePressEvent(self, event):
        """Allow dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_position'):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()