"""
Style management for the application
"""

class StyleManager:
    """Manage application styles and themes"""
    
    _dark_mode = False
    
    # Color schemes
    COLORS = {
        'light': {
            'background': '#f5f5f5',
            'card_background': '#ffffff',
            'text': '#333333',
            'text_secondary': '#666666',
            'border': '#dddddd',
            'primary': '#2196F3',
            'primary_hover': '#1976D2',
            'success': '#4CAF50',
            'success_light': '#E8F5E9',
            'warning': '#FF9800',
            'warning_light': '#FFF3E0',
            'danger': '#F44336',
            'danger_light': '#FFEBEE',
            'free': '#4CAF50',
            'running': '#2196F3',
            'overdue': '#F44336',
        },
        'dark': {
            'background': '#1a1a2e',
            'card_background': '#16213e',
            'text': '#eaeaea',
            'text_secondary': '#a0a0a0',
            'border': '#0f3460',
            'primary': '#e94560',
            'primary_hover': '#ff6b6b',
            'success': '#00d9ff',
            'success_light': '#1a3a4a',
            'warning': '#ffc107',
            'warning_light': '#3d3a1a',
            'danger': '#ff4757',
            'danger_light': '#3d1a1a',
            'free': '#00d9ff',
            'running': '#ffc107',
            'overdue': '#ff4757',
        }
    }
    
    @classmethod
    def toggle_dark_mode(cls):
        """Toggle dark mode"""
        cls._dark_mode = not cls._dark_mode
        return cls._dark_mode
    
    @classmethod
    def is_dark_mode(cls):
        """Check if dark mode is enabled"""
        return cls._dark_mode
    
    @classmethod
    def set_dark_mode(cls, enabled: bool):
        """Set dark mode"""
        cls._dark_mode = enabled
    
    @classmethod
    def get_colors(cls):
        """Get current color scheme"""
        return cls.COLORS['dark'] if cls._dark_mode else cls.COLORS['light']
    
    @classmethod
    def get_main_stylesheet(cls):
        """Get main application stylesheet"""
        colors = cls.get_colors()
        
        return f"""
            QMainWindow {{
                background-color: {colors['background']};
            }}
            
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: {colors['text']};
            }}
            
            QLabel {{
                color: {colors['text']};
            }}
            
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_secondary']};
            }}
            
            QPushButton.success {{
                background-color: {colors['success']};
            }}
            
            QPushButton.success:hover {{
                background-color: #45a049;
            }}
            
            QPushButton.danger {{
                background-color: {colors['danger']};
            }}
            
            QPushButton.danger:hover {{
                background-color: #da190b;
            }}
            
            QPushButton.secondary {{
                background-color: {colors['text_secondary']};
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                padding: 10px;
                border: 2px solid {colors['border']};
                border-radius: 5px;
                background-color: {colors['card_background']};
                color: {colors['text']};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {colors['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['text']};
                margin-right: 10px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: {colors['background']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['text_secondary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 5px;
                background-color: {colors['card_background']};
            }}
            
            QTabBar::tab {{
                padding: 10px 20px;
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['card_background']};
                border-bottom: 2px solid {colors['primary']};
            }}
            
            QTableWidget {{
                background-color: {colors['card_background']};
                border: 1px solid {colors['border']};
                border-radius: 5px;
                gridline-color: {colors['border']};
            }}
            
            QTableWidget::item {{
                padding: 8px;
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {colors['background']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {colors['primary']};
                font-weight: bold;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            QDialog {{
                background-color: {colors['card_background']};
            }}
            
            QMessageBox {{
                background-color: {colors['card_background']};
            }}
        """
    
    @classmethod
    def get_card_stylesheet(cls, status: str = 'free'):
        """Get stylesheet for playstation card"""
        colors = cls.get_colors()
        
        status_colors = {
            'free': colors['free'],
            'running': colors['running'],
            'overdue': colors['overdue']
        }
        
        status_color = status_colors.get(status, colors['free'])
        
        return f"""
            QFrame#card {{
                background-color: {colors['card_background']};
                border: 3px solid {status_color};
                border-radius: 15px;
            }}
            
            QLabel#title {{
                font-size: 20px;
                font-weight: bold;
                color: {colors['text']};
            }}
            
            QLabel#status {{
                font-size: 14px;
                font-weight: bold;
                color: {status_color};
                text-transform: uppercase;
            }}
            
            QLabel#timer {{
                font-size: 36px;
                font-weight: bold;
                color: {status_color};
                font-family: 'Consolas', monospace;
            }}
            
            QLabel#info {{
                font-size: 12px;
                color: {colors['text_secondary']};
            }}
            
            QLabel#price {{
                font-size: 18px;
                font-weight: bold;
                color: {colors['text']};
            }}
        """
    
    @classmethod
    def get_dialog_stylesheet(cls):
        """Get stylesheet for dialogs"""
        colors = cls.get_colors()
        
        return f"""
            QDialog {{
                background-color: {colors['card_background']};
            }}
            
            QLabel {{
                color: {colors['text']};
            }}
            
            QLabel#title {{
                font-size: 24px;
                font-weight: bold;
                color: {colors['text']};
                padding: 10px;
            }}
            
            QRadioButton {{
                color: {colors['text']};
                spacing: 10px;
            }}
            
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors['primary']};
                border: 2px solid {colors['primary']};
                border-radius: 10px;
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: transparent;
                border: 2px solid {colors['border']};
                border-radius: 10px;
            }}
        """