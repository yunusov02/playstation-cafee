"""
Dashboard widget with playstation grid
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer

from controllers import PlaystationController, SessionController, JoystickController
from views.playstation_card import PlaystationCard
from views.session_dialogs import StartSessionDialog, ModifySessionDialog, EndSessionDialog
from utils import StyleManager, format_currency, SoundManager
from config import GRID_SPACING


class DashboardWidget(QWidget):
    """Main dashboard showing all playstations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}  # playstation_id -> PlaystationCard
        
        self.setup_ui()
        self.load_playstations()
        
        # Refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.check_sessions)
        self.refresh_timer.start(5000)  # Check every 5 seconds
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🎮 Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Stats
        self.stats_frame = QFrame()
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setSpacing(30)
        
        self.active_sessions_label = QLabel("Active: 0")
        self.active_sessions_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.active_sessions_label)
        
        self.available_joysticks_label = QLabel("🎮 Available: 0")
        self.available_joysticks_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.available_joysticks_label)
        
        header_layout.addWidget(self.stats_frame)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_playstations)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(GRID_SPACING)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)
    
    def load_playstations(self):
        """Load all playstations and create cards"""
        # Clear existing cards
        for card in self.cards.values():
            card.deleteLater()
        self.cards.clear()
        
        # Clear grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load playstations
        playstations = PlaystationController.get_all_playstations()
        
        # Calculate grid columns based on widget width
        cols = max(1, self.width() // 300) if self.width() > 0 else 3
        
        for i, ps in enumerate(playstations):
            card = PlaystationCard(ps, self)
            card.start_session_clicked.connect(self.on_start_session)
            card.modify_session_clicked.connect(self.on_modify_session)
            card.end_session_clicked.connect(self.on_end_session)
            
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col)
            self.cards[ps.id] = card
        
        self.update_stats()
    
    def update_stats(self):
        """Update dashboard stats"""
        active = len(SessionController.get_all_active_sessions())
        available = JoystickController.get_available_count()
        total = JoystickController.get_total_count()
        
        self.active_sessions_label.setText(f"Active Sessions: {active}")
        self.available_joysticks_label.setText(f"🎮 Joysticks: {available}/{total}")
    
    def check_sessions(self):
        """Check for overdue sessions and play sound"""
        SessionController.check_overdue_sessions()
        
        for ps_id, card in self.cards.items():
            card.refresh()
        
        self.update_stats()
    
    def on_start_session(self, playstation_id: int):
        """Handle start session"""
        ps = PlaystationController.get_playstation(playstation_id)
        if not ps:
            return
        
        dialog = StartSessionDialog(
            playstation_id=playstation_id,
            ps_name=ps.name,
            ps_price=ps.price_per_hour,
            parent=self
        )
        
        if dialog.exec():
            SoundManager.play_start()
            if playstation_id in self.cards:
                self.cards[playstation_id].refresh()
            self.update_stats()
    
    def on_modify_session(self, playstation_id: int):
        """Handle modify session"""
        ps = PlaystationController.get_playstation(playstation_id)
        if not ps:
            return
        
        dialog = ModifySessionDialog(
            playstation_id=playstation_id,
            ps_name=ps.name,
            parent=self
        )
        
        if dialog.exec():
            if playstation_id in self.cards:
                self.cards[playstation_id].refresh()
            self.update_stats()
    
    def on_end_session(self, playstation_id: int):
        """Handle end session"""
        ps = PlaystationController.get_playstation(playstation_id)
        if not ps:
            return
        
        dialog = EndSessionDialog(
            playstation_id=playstation_id,
            ps_name=ps.name,
            parent=self
        )
        
        if dialog.exec():
            SoundManager.play_end()
            if playstation_id in self.cards:
                self.cards[playstation_id].refresh()
            self.update_stats()
    
    def resizeEvent(self, event):
        """Handle resize to reflow grid"""
        super().resizeEvent(event)
        # Reload to adjust grid columns
        if hasattr(self, 'cards') and self.cards:
            self.load_playstations()