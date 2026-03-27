from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from models import Playstation, PlaystationStatus, SessionType
from controllers import SessionController
from utils import StyleManager, format_time, format_currency
from config import CARD_WIDTH, CARD_HEIGHT
from utils.sound_manager import SoundManager


class PlaystationCard(QFrame):
    """Card widget displaying playstation status"""
    
    # Signals
    start_session_clicked = pyqtSignal(int)  # playstation_id
    modify_session_clicked = pyqtSignal(int)  # playstation_id
    end_session_clicked = pyqtSignal(int)  # playstation_id
    
    def __init__(self, playstation: Playstation, parent=None):
        super().__init__(parent)
        self.playstation = playstation
        self.session_info = None
        
        self.setObjectName("card")
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        
        self.setup_ui()
        self.update_display()
        
        # Timer for live updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_timer_display)
        self.update_timer.start(1000)  # Update every 2 seconds

        self.waring_played = False
        self.end_played = False
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Header: Name and Model
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.playstation.name)
        self.name_label.setObjectName("title")
        header_layout.addWidget(self.name_label)
        
        self.model_label = QLabel(self.playstation.model)
        self.model_label.setObjectName("info")
        self.model_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(self.model_label)
        
        layout.addLayout(header_layout)
        
        # Status
        self.status_label = QLabel("Свободен")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timer")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)
        
        # Session info
        info_layout = QHBoxLayout()
        
        self.joystick_label = QLabel("🎮 2")
        self.joystick_label.setObjectName("info")
        info_layout.addWidget(self.joystick_label)
        
        info_layout.addStretch()
        
        self.session_type_label = QLabel("")
        self.session_type_label.setObjectName("info")
        info_layout.addWidget(self.session_type_label)
        
        layout.addLayout(info_layout)
        
        # Current price
        self.price_label = QLabel("0 UZS")
        self.price_label.setObjectName("price")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.start_btn = QPushButton("Начать")
        self.start_btn.setProperty("class", "success")
        self.start_btn.clicked.connect(self._on_start_clicked)
        buttons_layout.addWidget(self.start_btn)
        
        self.modify_btn = QPushButton("Изменить")
        self.modify_btn.setProperty("class", "warning")
        self.modify_btn.clicked.connect(self._on_modify_clicked)
        buttons_layout.addWidget(self.modify_btn)
        
        self.end_btn = QPushButton("Завершить")
        self.end_btn.setProperty("class", "danger")
        self.end_btn.clicked.connect(self._on_end_clicked)
        buttons_layout.addWidget(self.end_btn)
        
        layout.addLayout(buttons_layout)
    
    def update_display(self):
        """Update display based on playstation status"""
        status = self.playstation.status.value
        self.setStyleSheet(StyleManager.get_card_stylesheet(status))
        
        self.status_label.setText(status.upper())
        
        # Get session info if running
        if self.playstation.status != PlaystationStatus.FREE:
            session = SessionController.get_active_session(self.playstation.id)
            if session:
                self.session_info = SessionController.get_session_info(session)
                self.joystick_label.setText(f"🎮 {session.current_joystick_count}")
                
                # Session type label
                type_labels = {
                    SessionType.HOURLY: "⏱️ Часовой",
                    SessionType.AMOUNT: "💰 Суммовый",
                    SessionType.VIP: "⭐ VIP"
                }
                self.session_type_label.setText(type_labels.get(session.session_type, ""))
            else:
                self.session_info = None
        else:
            self.session_info = None
            self.joystick_label.setText("🎮 2")
            self.session_type_label.setText("")
            self.timer_label.setText("00:00:00")
            self.price_label.setText("0 UZS")
        
        # Update button visibility
        is_free = self.playstation.status == PlaystationStatus.FREE
        self.start_btn.setVisible(is_free)
        self.modify_btn.setVisible(not is_free)
        self.end_btn.setVisible(not is_free)
    
    def update_timer_display(self):
        """Update timer display (called every second)"""
        if self.session_info is None:
            return
        
        # Calculate times
        elapsed = self.session_info['elapsed_seconds']
        remaining = self.session_info.get('remaining_seconds')
        current_price = self.session_info.get('current_price', 0)
        
        # Update based on session type
        session_type = self.session_info.get('session_type')
        
        if session_type == SessionType.VIP:
            # Show elapsed time for VIP
            self.timer_label.setText(format_time(elapsed))
        elif remaining is not None:
            # Show remaining time for hourly/amount
            if remaining < 0:
                self.timer_label.setStyleSheet("color: #F44336;")  # Red for overdue
                
                if not self.end_played:
                    SoundManager.play_timeout()
                    SoundManager.play_timeout()
                    SoundManager.play_timeout()
                    self.end_played = True
            elif remaining < 300:
                self.timer_label.setStyleSheet("color: #FF9800;")  # Orange for warning

                if not self.waring_played:
                    SoundManager.play_warning()
                    SoundManager.play_warning()
                    SoundManager.play_warning()
                    self.waring_played = True

            self.timer_label.setText(format_time(remaining))
        else:
            self.timer_label.setText(format_time(elapsed))
        
        # Update price (recalculate in real-time)
        session = SessionController.get_active_session(self.playstation.id)
        if session:
            current_price = SessionController.calculate_current_price(session)
            self.price_label.setText(format_currency(current_price))
            
            # Update session info for next tick
            self.session_info = SessionController.get_session_info(session)
            
            # Check if overdue
            if self.session_info.get('is_overdue') and self.playstation.status != PlaystationStatus.OVERDUE:
                from controllers import PlaystationController
                PlaystationController.update_status(self.playstation.id, PlaystationStatus.OVERDUE)
                self.playstation.status = PlaystationStatus.OVERDUE
                self.update_display()
    
    def refresh(self):
        """Refresh card data"""
        from controllers import PlaystationController
        self.playstation = PlaystationController.get_playstation(self.playstation.id)
        if self.playstation:
            self.update_display()
    
    def _on_start_clicked(self):
        self.start_session_clicked.emit(self.playstation.id)
    
    def _on_modify_clicked(self):
        self.modify_session_clicked.emit(self.playstation.id)
    
    def _on_end_clicked(self):
        self.end_session_clicked.emit(self.playstation.id)