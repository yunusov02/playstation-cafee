"""
Settings widget for application configuration
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from utils import StyleManager, SoundManager
from config import (
    DEFAULT_PS_HOUR_PRICE, DEFAULT_JOYSTICK_HOUR_PRICE,
    FREE_JOYSTICKS_PER_SESSION, MAX_JOYSTICKS_PER_SESSION
)


class SettingsWidget(QWidget):
    """Widget for application settings"""
    
    theme_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Appearance settings
        appearance_group = QGroupBox("🎨 Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.toggled.connect(self.toggle_dark_mode)
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        layout.addWidget(appearance_group)
        
        # Sound settings
        sound_group = QGroupBox("🔊 Sound")
        sound_layout = QVBoxLayout(sound_group)
        
        self.sound_enabled_checkbox = QCheckBox("Enable sound effects")
        self.sound_enabled_checkbox.toggled.connect(self.toggle_sound)
        sound_layout.addWidget(self.sound_enabled_checkbox)
        
        layout.addWidget(sound_group)
        
        # Pricing settings
        pricing_group = QGroupBox("💰 Default Pricing")
        pricing_layout = QVBoxLayout(pricing_group)
        
        ps_price_layout = QHBoxLayout()
        ps_price_layout.addWidget(QLabel("PlayStation price per hour:"))
        self.ps_price_spin = QDoubleSpinBox()
        self.ps_price_spin.setRange(1000, 100000)
        self.ps_price_spin.setSingleStep(1000)
        self.ps_price_spin.setValue(DEFAULT_PS_HOUR_PRICE)
        self.ps_price_spin.setSuffix(" UZS")
        ps_price_layout.addWidget(self.ps_price_spin)
        ps_price_layout.addStretch()
        pricing_layout.addLayout(ps_price_layout)
        
        joy_price_layout = QHBoxLayout()
        joy_price_layout.addWidget(QLabel("Joystick price per hour:"))
        self.joy_price_spin = QDoubleSpinBox()
        self.joy_price_spin.setRange(500, 50000)
        self.joy_price_spin.setSingleStep(500)
        self.joy_price_spin.setValue(DEFAULT_JOYSTICK_HOUR_PRICE)
        self.joy_price_spin.setSuffix(" UZS")
        joy_price_layout.addWidget(self.joy_price_spin)
        joy_price_layout.addStretch()
        pricing_layout.addLayout(joy_price_layout)
        
        layout.addWidget(pricing_group)
        
        # Session settings
        session_group = QGroupBox("🎮 Session Settings")
        session_layout = QVBoxLayout(session_group)
        
        free_joy_layout = QHBoxLayout()
        free_joy_layout.addWidget(QLabel("Free joysticks per session:"))
        self.free_joy_spin = QSpinBox()
        self.free_joy_spin.setRange(0, 5)
        self.free_joy_spin.setValue(FREE_JOYSTICKS_PER_SESSION)
        free_joy_layout.addWidget(self.free_joy_spin)
        free_joy_layout.addStretch()
        session_layout.addLayout(free_joy_layout)
        
        max_joy_layout = QHBoxLayout()
        max_joy_layout.addWidget(QLabel("Maximum joysticks per session:"))
        self.max_joy_spin = QSpinBox()
        self.max_joy_spin.setRange(2, 10)
        self.max_joy_spin.setValue(MAX_JOYSTICKS_PER_SESSION)
        max_joy_layout.addWidget(self.max_joy_spin)
        max_joy_layout.addStretch()
        session_layout.addLayout(max_joy_layout)
        
        layout.addWidget(session_group)
        
        layout.addStretch()
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setProperty("class", "success")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
    
    def load_settings(self):
        """Load current settings"""
        self.dark_mode_checkbox.setChecked(StyleManager.is_dark_mode())
        self.sound_enabled_checkbox.setChecked(SoundManager.is_enabled())
    
    def toggle_dark_mode(self, enabled: bool):
        """Toggle dark mode"""
        StyleManager.set_dark_mode(enabled)
        self.theme_changed.emit()
    
    def toggle_sound(self, enabled: bool):
        """Toggle sound effects"""
        SoundManager.set_enabled(enabled)
    
    def save_settings(self):
        """Save settings"""
        # In a real app, you would save these to a config file or database
        QMessageBox.information(
            self, "Settings Saved",
            "Settings have been saved successfully!"
        )


# Complete the AddEditDialog get_values method from management_widget.py