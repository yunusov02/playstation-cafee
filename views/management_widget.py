"""
Management widget for playstations, joysticks, and users
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QSpinBox,
    QMessageBox, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt

from controllers import PlaystationController, JoystickController, AuthController
from utils import StyleManager, format_currency
from config import DEFAULT_PS_HOUR_PRICE, DEFAULT_JOYSTICK_HOUR_PRICE


class ManagementWidget(QWidget):
    """Widget for managing playstations, joysticks, and users"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Playstations tab
        ps_tab = QWidget()
        ps_layout = QVBoxLayout(ps_tab)
        
        ps_btn_layout = QHBoxLayout()
        add_ps_btn = QPushButton("➕ Add Playstation")
        add_ps_btn.clicked.connect(self.add_playstation)
        ps_btn_layout.addWidget(add_ps_btn)
        
        refresh_ps_btn = QPushButton("🔄 Refresh")
        refresh_ps_btn.clicked.connect(self.load_playstations)
        ps_btn_layout.addWidget(refresh_ps_btn)
        
        ps_btn_layout.addStretch()
        ps_layout.addLayout(ps_btn_layout)
        
        self.ps_table = QTableWidget()
        self.ps_table.setColumnCount(5)
        self.ps_table.setHorizontalHeaderLabels(["ID", "Name", "Model", "Price/Hour", "Actions"])
        self.ps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ps_table.setAlternatingRowColors(True)
        self.ps_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        ps_layout.addWidget(self.ps_table)
        
        tabs.addTab(ps_tab, "🎮 Playstations")
        
        # Joysticks tab
        joy_tab = QWidget()
        joy_layout = QVBoxLayout(joy_tab)
        
        joy_btn_layout = QHBoxLayout()
        add_joy_btn = QPushButton("➕ Add Joystick")
        add_joy_btn.clicked.connect(self.add_joystick)
        joy_btn_layout.addWidget(add_joy_btn)
        
        refresh_joy_btn = QPushButton("🔄 Refresh")
        refresh_joy_btn.clicked.connect(self.load_joysticks)
        joy_btn_layout.addWidget(refresh_joy_btn)
        
        joy_btn_layout.addStretch()
        
        # Joystick stats
        self.joy_stats_label = QLabel("Available: 0 / Total: 0")
        joy_btn_layout.addWidget(self.joy_stats_label)
        
        joy_layout.addLayout(joy_btn_layout)
        
        self.joy_table = QTableWidget()
        self.joy_table.setColumnCount(6)
        self.joy_table.setHorizontalHeaderLabels(["ID", "Name", "Model", "Price/Hour", "Status", "Actions"])
        self.joy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.joy_table.setAlternatingRowColors(True)
        self.joy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        joy_layout.addWidget(self.joy_table)
        
        tabs.addTab(joy_tab, "🕹️ Joysticks")
        
        # Users tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        users_btn_layout = QHBoxLayout()
        add_user_btn = QPushButton("➕ Add Admin")
        add_user_btn.clicked.connect(self.add_user)
        users_btn_layout.addWidget(add_user_btn)
        
        refresh_users_btn = QPushButton("🔄 Refresh")
        refresh_users_btn.clicked.connect(self.load_users)
        users_btn_layout.addWidget(refresh_users_btn)
        
        users_btn_layout.addStretch()
        users_layout.addLayout(users_btn_layout)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Full Name", "Username", "Last Login", "Actions"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        users_layout.addWidget(self.users_table)
        
        tabs.addTab(users_tab, "👥 Admins")
        
        layout.addWidget(tabs)
    
    def load_data(self):
        """Load all data"""
        self.load_playstations()
        self.load_joysticks()
        self.load_users()
    
    def load_playstations(self):
        """Load playstations into table"""
        playstations = PlaystationController.get_all_playstations()
        self.ps_table.setRowCount(len(playstations))
        
        for i, ps in enumerate(playstations):
            self.ps_table.setItem(i, 0, QTableWidgetItem(str(ps.id)))
            self.ps_table.setItem(i, 1, QTableWidgetItem(ps.name))
            self.ps_table.setItem(i, 2, QTableWidgetItem(ps.model))
            self.ps_table.setItem(i, 3, QTableWidgetItem(format_currency(ps.price_per_hour)))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedWidth(80)
            edit_btn.clicked.connect(lambda checked, pid=ps.id: self.edit_playstation(pid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedWidth(80)
            delete_btn.setStyleSheet("background-color: #F44336;")
            delete_btn.clicked.connect(lambda checked, pid=ps.id: self.delete_playstation(pid))
            actions_layout.addWidget(delete_btn)
            
            actions_layout.addStretch()
            
            self.ps_table.setCellWidget(i, 4, actions_widget)
        
        self.ps_table.resizeRowsToContents()
    
    def load_joysticks(self):
        """Load joysticks into table"""
        joysticks = JoystickController.get_all_joysticks()
        self.joy_table.setRowCount(len(joysticks))
        
        available = JoystickController.get_available_count()
        total = JoystickController.get_total_count()
        self.joy_stats_label.setText(f"Available: {available} / Total: {total}")
        
        for i, joy in enumerate(joysticks):
            self.joy_table.setItem(i, 0, QTableWidgetItem(str(joy.id)))
            self.joy_table.setItem(i, 1, QTableWidgetItem(joy.name))
            self.joy_table.setItem(i, 2, QTableWidgetItem(joy.model))
            self.joy_table.setItem(i, 3, QTableWidgetItem(format_currency(joy.price_per_hour)))
            
            # Status with color
            status_item = QTableWidgetItem(joy.status.value.upper())
            if joy.status.value == "available":
                status_item.setBackground(Qt.GlobalColor.green)
            elif joy.status.value == "in_use":
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setBackground(Qt.GlobalColor.red)
            self.joy_table.setItem(i, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedWidth(80)
            edit_btn.clicked.connect(lambda checked, jid=joy.id: self.edit_joystick(jid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedWidth(80)
            delete_btn.setStyleSheet("background-color: #F44336;")
            delete_btn.clicked.connect(lambda checked, jid=joy.id: self.delete_joystick(jid))
            actions_layout.addWidget(delete_btn)
            
            actions_layout.addStretch()
            
            self.joy_table.setCellWidget(i, 5, actions_widget)
        
        self.joy_table.resizeRowsToContents()
    
    def load_users(self):
        """Load users into table"""
        users = AuthController.get_all_users()
        self.users_table.setRowCount(len(users))
        
        current_user = AuthController.get_current_user()
        
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(i, 1, QTableWidgetItem(user.full_name))
            self.users_table.setItem(i, 2, QTableWidgetItem(user.username))
            
            # Last login
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
            self.users_table.setItem(i, 3, QTableWidgetItem(last_login))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedWidth(80)
            edit_btn.clicked.connect(lambda checked, uid=user.id: self.edit_user(uid))
            actions_layout.addWidget(edit_btn)
            
            # Don't allow deleting own account
            if current_user and user.id != current_user.id:
                delete_btn = QPushButton("🗑️ Delete")
                delete_btn.setFixedWidth(80)
                delete_btn.setStyleSheet("background-color: #F44336;")
                delete_btn.clicked.connect(lambda checked, uid=user.id: self.delete_user(uid))
                actions_layout.addWidget(delete_btn)
            
            actions_layout.addStretch()
            
            self.users_table.setCellWidget(i, 4, actions_widget)
        
        self.users_table.resizeRowsToContents()
    
    # ============== PLAYSTATION CRUD ==============
    
    def add_playstation(self):
        """Add new playstation"""
        dialog = AddEditDialog("Add Playstation", [
            ("Name", "text", ""),
            ("Model", "combo", ["PS5", "PS4", "PS4 Pro", "PS3"]),
            ("Price/Hour", "number", DEFAULT_PS_HOUR_PRICE)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Name"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = PlaystationController.create_playstation(
                name=values["Name"].strip(),
                model=values["Model"],
                price_per_hour=values["Price/Hour"]
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_playstations()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def edit_playstation(self, ps_id: int):
        """Edit playstation"""
        ps = PlaystationController.get_playstation(ps_id)
        if not ps:
            QMessageBox.warning(self, "Error", "Playstation not found!")
            return
        
        dialog = AddEditDialog("Edit Playstation", [
            ("Name", "text", ps.name),
            ("Model", "combo", ["PS5", "PS4", "PS4 Pro", "PS3"], ps.model),
            ("Price/Hour", "number", ps.price_per_hour)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Name"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = PlaystationController.update_playstation(
                ps_id=ps_id,
                name=values["Name"].strip(),
                model=values["Model"],
                price_per_hour=values["Price/Hour"]
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_playstations()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_playstation(self, ps_id: int):
        """Delete playstation"""
        ps = PlaystationController.get_playstation(ps_id)
        if not ps:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{ps.name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = PlaystationController.delete_playstation(ps_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_playstations()
            else:
                QMessageBox.warning(self, "Error", message)
    
    # ============== JOYSTICK CRUD ==============
    
    def add_joystick(self):
        """Add new joystick"""
        dialog = AddEditDialog("Add Joystick", [
            ("Name", "text", ""),
            ("Model", "combo", ["DualSense", "DualShock 4", "DualShock 3"]),
            ("Price/Hour", "number", DEFAULT_JOYSTICK_HOUR_PRICE)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Name"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = JoystickController.create_joystick(
                name=values["Name"].strip(),
                model=values["Model"],
                price_per_hour=values["Price/Hour"]
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_joysticks()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def edit_joystick(self, joy_id: int):
        """Edit joystick"""
        from database import get_db
        from models import Joystick
        
        db = get_db()
        joystick = db.query(Joystick).filter(Joystick.id == joy_id).first()
        
        if not joystick:
            QMessageBox.warning(self, "Error", "Joystick not found!")
            return
        
        dialog = AddEditDialog("Edit Joystick", [
            ("Name", "text", joystick.name),
            ("Model", "combo", ["DualSense", "DualShock 4", "DualShock 3"], joystick.model),
            ("Price/Hour", "number", joystick.price_per_hour)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Name"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = JoystickController.update_joystick(
                joystick_id=joy_id,
                name=values["Name"].strip(),
                model=values["Model"],
                price_per_hour=values["Price/Hour"]
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_joysticks()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_joystick(self, joy_id: int):
        """Delete joystick"""
        from database import get_db
        from models import Joystick
        
        db = get_db()
        joystick = db.query(Joystick).filter(Joystick.id == joy_id).first()
        
        if not joystick:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{joystick.name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = JoystickController.delete_joystick(joy_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_joysticks()
            else:
                QMessageBox.warning(self, "Error", message)
    
    # ============== USER CRUD ==============
    
    def add_user(self):
        """Add new user"""
        dialog = AddEditDialog("Add Admin User", [
            ("Full Name", "text", ""),
            ("Username", "text", ""),
            ("Password", "password", "")
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            
            # Validation
            if not values["Full Name"].strip():
                QMessageBox.warning(self, "Error", "Full Name is required!")
                return
            if not values["Username"].strip():
                QMessageBox.warning(self, "Error", "Username is required!")
                return
            if not values["Password"]:
                QMessageBox.warning(self, "Error", "Password is required!")
                return
            if len(values["Password"]) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters!")
                return
                
            success, message = AuthController.create_user(
                full_name=values["Full Name"].strip(),
                username=values["Username"].strip(),
                password=values["Password"]
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def edit_user(self, user_id: int):
        """Edit user"""
        from database import get_db
        from models import User
        
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            QMessageBox.warning(self, "Error", "User not found!")
            return
        
        dialog = EditUserDialog(user, self)
        
        if dialog.exec():
            values = dialog.get_values()
            
            if not values["Full Name"].strip():
                QMessageBox.warning(self, "Error", "Full Name is required!")
                return
            
            # Check if password should be updated
            new_password = values.get("New Password", "")
            if new_password and len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters!")
                return
                
            success, message = AuthController.update_user(
                user_id=user_id,
                full_name=values["Full Name"].strip(),
                password=new_password if new_password else None
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_user(self, user_id: int):
        """Delete (deactivate) user"""
        from database import get_db
        from models import User
        
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return
        
        current_user = AuthController.get_current_user()
        if current_user and user.id == current_user.id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account!")
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete user '{user.username}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = AuthController.deactivate_user(user_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", message)


class AddEditDialog(QDialog):
    """Generic add/edit dialog for creating and modifying records"""
    
    def __init__(self, title: str, fields: list, parent=None):
        """
        Initialize the dialog
        
        Args:
            title: Dialog title
            fields: List of tuples defining fields
                    Format: (name, type, default_value, [options for combo])
                    Types: "text", "password", "number", "combo", "spin"
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.fields = {}
        self.setup_ui(title, fields)
        self.apply_styles()
    
    def setup_ui(self, title: str, fields: list):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        for field in fields:
            name = field[0]
            field_type = field[1]
            default = field[2] if len(field) > 2 else ""
            
            if field_type == "text":
                widget = QLineEdit()
                widget.setText(str(default) if default else "")
                widget.setMinimumHeight(35)
                
            elif field_type == "password":
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.EchoMode.Password)
                widget.setMinimumHeight(35)
                widget.setPlaceholderText("Enter password...")
                
            elif field_type == "number":
                widget = QDoubleSpinBox()
                widget.setRange(0, 10000000)
                widget.setDecimals(0)
                widget.setSingleStep(1000)
                widget.setValue(float(default) if default else 0)
                widget.setMinimumHeight(35)
                widget.setSuffix(" UZS")
                
            elif field_type == "spin":
                widget = QSpinBox()
                widget.setRange(0, 1000)
                widget.setValue(int(default) if default else 0)
                widget.setMinimumHeight(35)
                
            elif field_type == "combo":
                widget = QComboBox()
                widget.setMinimumHeight(35)
                # default can be a list of options
                if isinstance(default, list):
                    widget.addItems(default)
                    # Check if there's a selected value (4th element)
                    if len(field) > 3:
                        widget.setCurrentText(field[3])
                else:
                    widget.addItem(str(default) if default else "")
                    
            else:
                widget = QLineEdit()
                widget.setText(str(default) if default else "")
                widget.setMinimumHeight(35)
            
            form_layout.addRow(f"{name}:", widget)
            self.fields[name] = widget
        
        layout.addLayout(form_layout)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setMinimumHeight(40)
        save_btn.setProperty("class", "success")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def apply_styles(self):
        """Apply dialog styles"""
        colors = StyleManager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['card_background']};
            }}
            
            QLabel {{
                color: {colors['text']};
                font-size: 14px;
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                padding: 8px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['background']};
                color: {colors['text']};
                font-size: 14px;
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {colors['primary']};
            }}
            
            QPushButton {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            
            QPushButton[class="success"] {{
                background-color: {colors['success']};
                color: white;
            }}
            
            QPushButton[class="success"]:hover {{
                background-color: #45a049;
            }}
            
            QPushButton[class="secondary"] {{
                background-color: {colors['border']};
                color: {colors['text']};
            }}
            
            QPushButton[class="secondary"]:hover {{
                background-color: {colors['text_secondary']};
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
            
            QComboBox QAbstractItemView {{
                background-color: {colors['card_background']};
                color: {colors['text']};
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
        """)
    
    def get_values(self) -> dict:
        """
        Get all field values as a dictionary
        
        Returns:
            dict: Dictionary with field names as keys and their values
        """
        values = {}
        
        for name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text()
            elif isinstance(widget, QDoubleSpinBox):
                values[name] = widget.value()
            elif isinstance(widget, QSpinBox):
                values[name] = widget.value()
            elif isinstance(widget, QComboBox):
                values[name] = widget.currentText()
            else:
                # Fallback for unknown widget types
                values[name] = None
        
        return values


class EditUserDialog(QDialog):
    """Special dialog for editing user with optional password change"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Edit User - {user.username}")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.fields = {}
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(f"✏️ Edit User: {self.user.username}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setText(self.user.full_name)
        self.full_name_input.setMinimumHeight(35)
        form_layout.addRow("Full Name:", self.full_name_input)
        self.fields["Full Name"] = self.full_name_input
        
        # Username (read-only)
        username_input = QLineEdit()
        username_input.setText(self.user.username)
        username_input.setReadOnly(True)
        username_input.setMinimumHeight(35)
        username_input.setStyleSheet("background-color: #e0e0e0;")
        form_layout.addRow("Username:", username_input)
        
        layout.addLayout(form_layout)
        
        # Password change section
        password_group = QFrame()
        password_group.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        password_layout = QVBoxLayout(password_group)
        
        password_title = QLabel("🔐 Change Password (Optional)")
        password_title.setStyleSheet("font-weight: bold; border: none;")
        password_layout.addWidget(password_title)
        
        password_note = QLabel("Leave empty to keep current password")
        password_note.setStyleSheet("color: gray; font-size: 12px; border: none;")
        password_layout.addWidget(password_note)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("New password (min 6 characters)")
        self.new_password_input.setMinimumHeight(35)
        password_layout.addWidget(self.new_password_input)
        self.fields["New Password"] = self.new_password_input
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setMinimumHeight(35)
        password_layout.addWidget(self.confirm_password_input)
        
        layout.addWidget(password_group)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        save_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def apply_styles(self):
        """Apply dialog styles"""
        colors = StyleManager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['card_background']};
            }}
            
            QLabel {{
                color: {colors['text']};
                font-size: 14px;
            }}
            
            QLineEdit {{
                padding: 8px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['background']};
                color: {colors['text']};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: {colors['primary']};
            }}
            
            QPushButton {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                background-color: {colors['border']};
                color: {colors['text']};
            }}
            
            QPushButton:hover {{
                background-color: {colors['text_secondary']};
            }}
        """)
    
    def validate_and_accept(self):
        """Validate form and accept dialog"""
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # If password fields are filled, validate them
        if new_password or confirm_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            if len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters!")
                return
        
        self.accept()
    
    def get_values(self) -> dict:
        """
        Get all field values as a dictionary
        
        Returns:
            dict: Dictionary with field names as keys and their values
        """
        return {
            "Full Name": self.full_name_input.text(),
            "New Password": self.new_password_input.text()
        }

