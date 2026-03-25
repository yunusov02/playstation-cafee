"""
Session management dialogs
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QSpinBox,
    QDoubleSpinBox, QGroupBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models import SessionType, PaymentType
from controllers import SessionController, AuthController, JoystickController
from utils import StyleManager, format_currency


class StartSessionDialog(QDialog):
    """Dialog for starting a new session"""
    
    def __init__(self, playstation_id: int, ps_name: str, ps_price: float, parent=None):
        super().__init__(parent)
        self.playstation_id = playstation_id
        self.ps_name = ps_name
        self.ps_price = ps_price
        
        self.setWindowTitle(f"Start Session - {ps_name}")
        self.setFixedWidth(450)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(f"🎮 Start Session on {self.ps_name}")
        title.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Session Type Selection
        type_group = QGroupBox("Session Type")
        type_layout = QVBoxLayout(type_group)
        
        self.type_button_group = QButtonGroup(self)
        
        # Hourly option
        hourly_layout = QHBoxLayout()
        self.hourly_radio = QRadioButton("⏱️ Fixed Hours")
        self.hourly_radio.setChecked(True)
        self.type_button_group.addButton(self.hourly_radio, 1)
        hourly_layout.addWidget(self.hourly_radio)
        
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0.5, 12)
        self.hours_spin.setSingleStep(0.5)
        self.hours_spin.setValue(1)
        self.hours_spin.setSuffix(" hours")
        self.hours_spin.valueChanged.connect(self._update_preview)
        hourly_layout.addWidget(self.hours_spin)
        
        type_layout.addLayout(hourly_layout)
        
        # Amount option
        amount_layout = QHBoxLayout()
        self.amount_radio = QRadioButton("💰 Fixed Amount")
        self.type_button_group.addButton(self.amount_radio, 2)
        amount_layout.addWidget(self.amount_radio)
        
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(5000, 500000)
        self.amount_spin.setSingleStep(5000)
        self.amount_spin.setValue(15000)
        self.amount_spin.setSuffix(" UZS")
        self.amount_spin.valueChanged.connect(self._update_preview)
        amount_layout.addWidget(self.amount_spin)
        
        type_layout.addLayout(amount_layout)
        
        # VIP option
        self.vip_radio = QRadioButton("⭐ VIP (Pay at end)")
        self.type_button_group.addButton(self.vip_radio, 3)
        type_layout.addWidget(self.vip_radio)
        
        layout.addWidget(type_group)
        
        # Joystick Selection
        joystick_group = QGroupBox("Joysticks")
        joystick_layout = QHBoxLayout(joystick_group)
        
        joystick_layout.addWidget(QLabel("Initial joysticks:"))
        
        self.joystick_spin = QSpinBox()
        self.joystick_spin.setRange(2, 5)
        self.joystick_spin.setValue(2)
        self.joystick_spin.valueChanged.connect(self._update_preview)
        joystick_layout.addWidget(self.joystick_spin)
        
        available = JoystickController.get_available_count()
        joystick_layout.addWidget(QLabel(f"(Available: {available + 2})"))  # +2 for free ones
        
        joystick_layout.addStretch()
        
        layout.addWidget(joystick_group)
        
        # Preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: rgba(0,0,0,0.05); border-radius: 10px; padding: 10px;")
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_frame)
        
        # Connect radio buttons
        self.hourly_radio.toggled.connect(self._on_type_changed)
        self.amount_radio.toggled.connect(self._on_type_changed)
        self.vip_radio.toggled.connect(self._on_type_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.start_btn = QPushButton("🎮 Start Session")
        self.start_btn.setProperty("class", "success")
        self.start_btn.clicked.connect(self.start_session)
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
        
        # Initial state
        self._on_type_changed()
        self._update_preview()
    
    def _on_type_changed(self):
        """Handle session type change"""
        self.hours_spin.setEnabled(self.hourly_radio.isChecked())
        self.amount_spin.setEnabled(self.amount_radio.isChecked())
        self._update_preview()
    
    def _update_preview(self):
        """Update price preview"""
        joysticks = self.joystick_spin.value()
        extra_joysticks = max(0, joysticks - 2)
        joystick_price = JoystickController.get_default_price()
        
        if self.hourly_radio.isChecked():
            hours = self.hours_spin.value()
            ps_cost = hours * self.ps_price
            joy_cost = hours * extra_joysticks * joystick_price
            total = ps_cost + joy_cost
            
            preview = f"<b>Session: {hours} hours</b><br>"
            preview += f"PlayStation: {format_currency(ps_cost)}<br>"
            if extra_joysticks > 0:
                preview += f"Extra joysticks ({extra_joysticks}): {format_currency(joy_cost)}<br>"
            preview += f"<b>Estimated Total: {format_currency(total)}</b>"
            
        elif self.amount_radio.isChecked():
            amount = self.amount_spin.value()
            rate = self.ps_price + extra_joysticks * joystick_price
            est_hours = amount / rate
            
            preview = f"<b>Budget: {format_currency(amount)}</b><br>"
            preview += f"<b>Estimated playtime: ~{est_hours:.1f} hours</b>"
            
        else:  # VIP
            preview = "<b>VIP Session</b><br>"
            preview += "Play unlimited time, pay at the end."
        
        self.preview_label.setText(preview)
    
    def apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(StyleManager.get_dialog_stylesheet())
    
    def start_session(self):
        """Start the session"""
        admin = AuthController.get_current_user()
        if not admin:
            QMessageBox.warning(self, "Error", "Not logged in")
            return
        
        # Determine session type and target value
        if self.hourly_radio.isChecked():
            session_type = SessionType.HOURLY
            target_value = self.hours_spin.value()
        elif self.amount_radio.isChecked():
            session_type = SessionType.AMOUNT
            target_value = self.amount_spin.value()
        else:
            session_type = SessionType.VIP
            target_value = None
        
        joysticks = self.joystick_spin.value()
        
        success, message, session = SessionController.start_session(
            playstation_id=self.playstation_id,
            admin_id=admin.id,
            session_type=session_type,
            target_value=target_value,
            initial_joysticks=joysticks
        )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)


class ModifySessionDialog(QDialog):
    """Dialog for modifying session joysticks"""
    
    def __init__(self, playstation_id: int, ps_name: str, parent=None):
        super().__init__(parent)
        self.playstation_id = playstation_id
        self.ps_name = ps_name
        
        self.setWindowTitle(f"Modify Session - {ps_name}")
        self.setFixedWidth(400)
        
        self.session = SessionController.get_active_session(playstation_id)
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(f"🎮 Modify Session - {self.ps_name}")
        title.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        if not self.session:
            layout.addWidget(QLabel("No active session found"))
            return
        
        # Current info
        info_group = QGroupBox("Current Session")
        info_layout = QVBoxLayout(info_group)
        
        current_joysticks = self.session.current_joystick_count
        info_layout.addWidget(QLabel(f"Current joysticks: {current_joysticks}"))
        
        session_info = SessionController.get_session_info(self.session)
        current_price = session_info.get('current_price', 0)
        info_layout.addWidget(QLabel(f"Current price: {format_currency(current_price)}"))
        
        layout.addWidget(info_group)
        
        # Modify joysticks
        modify_group = QGroupBox("Modify Joysticks")
        modify_layout = QHBoxLayout(modify_group)
        
        modify_layout.addWidget(QLabel("New joystick count:"))
        
        self.joystick_spin = QSpinBox()
        self.joystick_spin.setRange(2, 5)
        self.joystick_spin.setValue(current_joysticks)
        modify_layout.addWidget(self.joystick_spin)
        
        available = JoystickController.get_available_count()
        max_available = current_joysticks + available
        if max_available > 5:
            max_available = 5
        self.joystick_spin.setMaximum(max_available)
        
        modify_layout.addStretch()
        
        layout.addWidget(modify_group)
        
        # Note
        note = QLabel("⚠️ Changing joysticks will create a new price segment")
        note.setStyleSheet("color: #FF9800; font-size: 12px;")
        note.setWordWrap(True)
        layout.addWidget(note)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(StyleManager.get_dialog_stylesheet())
    
    def save_changes(self):
        """Save joystick changes"""
        if not self.session:
            self.reject()
            return
        
        new_count = self.joystick_spin.value()
        
        success, message = SessionController.modify_session_joysticks(
            self.session.id, new_count
        )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)


class EndSessionDialog(QDialog):
    """Dialog for ending a session"""
    
    def __init__(self, playstation_id: int, ps_name: str, parent=None):
        super().__init__(parent)
        self.playstation_id = playstation_id
        self.ps_name = ps_name
        
        self.setWindowTitle(f"End Session - {ps_name}")
        self.setFixedWidth(450)
        
        self.session = SessionController.get_active_session(playstation_id)
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(f"💰 End Session - {self.ps_name}")
        title.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        if not self.session:
            layout.addWidget(QLabel("No active session found"))
            return
        
        # Session summary
        summary_group = QGroupBox("Session Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        session_info = SessionController.get_session_info(self.session)
        
        # Duration
        elapsed = session_info.get('elapsed_seconds', 0)
        hours = elapsed / 3600
        summary_layout.addWidget(QLabel(f"⏱️ Duration: {hours:.2f} hours"))
        
        # Segments breakdown
        summary_layout.addWidget(QLabel("\n📊 Segments:"))
        for i, segment in enumerate(self.session.segments, 1):
            seg_hours = segment.duration_hours
            seg_price = segment.calculate_price()
            summary_layout.addWidget(QLabel(
                f"  {i}. {seg_hours:.2f}h × {segment.joystick_count} joysticks = {format_currency(seg_price)}"
            ))
        
        # Total
        self.total_price = SessionController.calculate_current_price(self.session)
        total_label = QLabel(f"\n💵 Total: {format_currency(self.total_price)}")
        total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        summary_layout.addWidget(total_label)
        
        layout.addWidget(summary_group)
        
        # Payment type
        payment_group = QGroupBox("Payment Method")
        payment_layout = QVBoxLayout(payment_group)
        
        self.payment_button_group = QButtonGroup(self)
        
        self.cash_radio = QRadioButton(f"💵 Cash - {format_currency(self.total_price)}")
        self.cash_radio.setChecked(True)
        self.payment_button_group.addButton(self.cash_radio, 1)
        payment_layout.addWidget(self.cash_radio)
        
        self.terminal_radio = QRadioButton(f"💳 Terminal - {format_currency(self.total_price)}")
        self.payment_button_group.addButton(self.terminal_radio, 2)
        payment_layout.addWidget(self.terminal_radio)
        
        self.hybrid_radio = QRadioButton("🔀 Hybrid (Split payment)")
        self.payment_button_group.addButton(self.hybrid_radio, 3)
        payment_layout.addWidget(self.hybrid_radio)
        
        # Hybrid amounts
        self.hybrid_frame = QFrame()
        hybrid_layout = QHBoxLayout(self.hybrid_frame)
        
        hybrid_layout.addWidget(QLabel("Cash:"))
        self.cash_spin = QSpinBox()
        self.cash_spin.setRange(0, int(self.total_price))
        self.cash_spin.setSingleStep(1000)
        self.cash_spin.setValue(int(self.total_price // 2))
        self.cash_spin.valueChanged.connect(self._update_terminal_amount)
        hybrid_layout.addWidget(self.cash_spin)
        
        hybrid_layout.addWidget(QLabel("Terminal:"))
        self.terminal_amount_label = QLabel()
        hybrid_layout.addWidget(self.terminal_amount_label)
        
        self.hybrid_frame.setVisible(False)
        payment_layout.addWidget(self.hybrid_frame)
        
        self.hybrid_radio.toggled.connect(self._on_hybrid_toggled)
        
        layout.addWidget(payment_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        end_btn = QPushButton("💰 Complete Payment")
        end_btn.setProperty("class", "success")
        end_btn.clicked.connect(self.end_session)
        button_layout.addWidget(end_btn)
        
        layout.addLayout(button_layout)
        
        self._update_terminal_amount()
    
    def _on_hybrid_toggled(self, checked):
        """Show/hide hybrid payment options"""
        self.hybrid_frame.setVisible(checked)
    
    def _update_terminal_amount(self):
        """Update terminal amount label"""
        cash = self.cash_spin.value()
        terminal = self.total_price - cash
        self.terminal_amount_label.setText(format_currency(terminal))
    
    def apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(StyleManager.get_dialog_stylesheet())
    
    def end_session(self):
        """End the session"""
        if not self.session:
            self.reject()
            return
        
        # Determine payment type and amounts
        if self.cash_radio.isChecked():
            payment_type = PaymentType.CASH
            cash_amount = self.total_price
            terminal_amount = 0
        elif self.terminal_radio.isChecked():
            payment_type = PaymentType.TERMINAL
            cash_amount = 0
            terminal_amount = self.total_price
        else:
            payment_type = PaymentType.HYBRID
            cash_amount = self.cash_spin.value()
            terminal_amount = self.total_price - cash_amount
        
        success, message, total = SessionController.end_session(
            session_id=self.session.id,
            payment_type=payment_type,
            cash_amount=cash_amount,
            terminal_amount=terminal_amount
        )
        
        if success:
            QMessageBox.information(
                self, "Session Ended",
                f"Session completed successfully!\n\nTotal: {format_currency(total)}"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)