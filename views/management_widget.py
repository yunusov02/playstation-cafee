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
        title = QLabel("⚙️ Управление")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Playstations tab
        ps_tab = QWidget()
        ps_layout = QVBoxLayout(ps_tab)
        
        ps_btn_layout = QHBoxLayout()
        add_ps_btn = QPushButton("➕ Добавить PlayStation")
        add_ps_btn.setStyleSheet(self._get_add_button_style())
        add_ps_btn.clicked.connect(self.add_playstation)
        ps_btn_layout.addWidget(add_ps_btn)
        
        refresh_ps_btn = QPushButton("🔄 Обновить")
        refresh_ps_btn.setStyleSheet(self._get_refresh_button_style())
        refresh_ps_btn.clicked.connect(self.load_playstations)
        ps_btn_layout.addWidget(refresh_ps_btn)
        
        ps_btn_layout.addStretch()
        ps_layout.addLayout(ps_btn_layout)
        
        self.ps_table = QTableWidget()
        self.ps_table.setColumnCount(5)
        self.ps_table.setHorizontalHeaderLabels(["ID", "Имя", "Модель", "Цена/час", "Действия"])
        self.ps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.ps_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.ps_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.ps_table.setColumnWidth(4, 220)
        self.ps_table.setAlternatingRowColors(True)
        self.ps_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ps_table.setStyleSheet(self._get_table_style())
        ps_layout.addWidget(self.ps_table)
        
        tabs.addTab(ps_tab, "🎮 PlayStation")
        
        # Joysticks tab
        joy_tab = QWidget()
        joy_layout = QVBoxLayout(joy_tab)
        
        joy_btn_layout = QHBoxLayout()
        add_joy_btn = QPushButton("➕ Добавить Joystick")
        add_joy_btn.setStyleSheet(self._get_add_button_style())
        add_joy_btn.clicked.connect(self.add_joystick)
        joy_btn_layout.addWidget(add_joy_btn)
        
        refresh_joy_btn = QPushButton("🔄 Обновить")
        refresh_joy_btn.setStyleSheet(self._get_refresh_button_style())
        refresh_joy_btn.clicked.connect(self.load_joysticks)
        joy_btn_layout.addWidget(refresh_joy_btn)
        
        joy_btn_layout.addStretch()
        
        # Joystick stats
        self.joy_stats_label = QLabel("Доступно: 0 / Всего: 0")
        self.joy_stats_label.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        joy_btn_layout.addWidget(self.joy_stats_label)
        
        joy_layout.addLayout(joy_btn_layout)
        
        self.joy_table = QTableWidget()
        self.joy_table.setColumnCount(5)
        self.joy_table.setHorizontalHeaderLabels(["ID", "Имя", "Модель", "Цена/час", "Действия"])
        self.joy_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.joy_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.joy_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.joy_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.joy_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.joy_table.setColumnWidth(4, 220)
        self.joy_table.setAlternatingRowColors(True)
        self.joy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.joy_table.setStyleSheet(self._get_table_style())
        joy_layout.addWidget(self.joy_table)
        
        tabs.addTab(joy_tab, "🕹️ Joysticks")
        
        # Users tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        users_btn_layout = QHBoxLayout()
        add_user_btn = QPushButton("➕ Добавить Admin")
        add_user_btn.setStyleSheet(self._get_add_button_style())
        add_user_btn.clicked.connect(self.add_user)
        users_btn_layout.addWidget(add_user_btn)
        
        refresh_users_btn = QPushButton("🔄 Обновить")
        refresh_users_btn.setStyleSheet(self._get_refresh_button_style())
        refresh_users_btn.clicked.connect(self.load_users)
        users_btn_layout.addWidget(refresh_users_btn)
        
        users_btn_layout.addStretch()
        users_layout.addLayout(users_btn_layout)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Имя пользователя", "Username", "Последний вход", "Действия"])
        self.users_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.users_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.users_table.setColumnWidth(4, 220)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setStyleSheet(self._get_table_style())
        users_layout.addWidget(self.users_table)
        
        tabs.addTab(users_tab, "👥 Пользователи")
        
        layout.addWidget(tabs)
    
    def _get_table_style(self):
        """Return table stylesheet"""
        return """
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F5F5F5;
                color: #333333;
                gridline-color: #E0E0E0;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #1976D2;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #333333;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #1976D2;
                font-weight: bold;
            }
        """
    
    def _get_add_button_style(self):
        """Return add button stylesheet"""
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
    
    def _get_refresh_button_style(self):
        """Return refresh button stylesheet"""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1976d2;
            }
        """
    
    def _get_edit_button_style(self):
        """Return edit button stylesheet"""
        return """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """
    
    def _get_delete_button_style(self):
        """Return delete button stylesheet"""
        return """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
        """
    
    def _create_action_buttons(self, edit_callback, delete_callback=None):
        """Create action buttons widget for table rows"""
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background-color: transparent;")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 5, 5, 5)
        actions_layout.setSpacing(8)
        
        edit_btn = QPushButton("✏️ Изменить")
        edit_btn.setStyleSheet(self._get_edit_button_style())
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(edit_callback)
        actions_layout.addWidget(edit_btn)
        
        if delete_callback:
            delete_btn = QPushButton("🗑️ Удалить")
            delete_btn.setStyleSheet(self._get_delete_button_style())
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(delete_callback)
            actions_layout.addWidget(delete_btn)
        
        actions_layout.addStretch()
        
        return actions_widget
    
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
            # Set row height
            self.ps_table.setRowHeight(i, 50)
            
            self.ps_table.setItem(i, 0, QTableWidgetItem(str(ps.id)))
            self.ps_table.setItem(i, 1, QTableWidgetItem(ps.name))
            self.ps_table.setItem(i, 2, QTableWidgetItem(ps.model))
            self.ps_table.setItem(i, 3, QTableWidgetItem(format_currency(ps.price_per_hour)))
            
            # Center align items
            for col in range(4):
                item = self.ps_table.item(i, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Actions
            actions_widget = self._create_action_buttons(
                lambda checked, pid=ps.id: self.edit_playstation(pid),
                lambda checked, pid=ps.id: self.delete_playstation(pid)
            )
            self.ps_table.setCellWidget(i, 4, actions_widget)
    
    def load_joysticks(self):
        """Load joysticks into table"""
        joysticks = JoystickController.get_all_joysticks()
        self.joy_table.setRowCount(len(joysticks))
        
        available = JoystickController.get_available_count()
        total = JoystickController.get_total_count()
        self.joy_stats_label.setText(f"Доступно: {available} / Всего: {total}")
        
        for i, joy in enumerate(joysticks):
            # Set row height
            self.joy_table.setRowHeight(i, 50)
            
            self.joy_table.setItem(i, 0, QTableWidgetItem(str(joy.id)))
            self.joy_table.setItem(i, 1, QTableWidgetItem(joy.name))
            self.joy_table.setItem(i, 2, QTableWidgetItem(joy.model))
            self.joy_table.setItem(i, 3, QTableWidgetItem(format_currency(joy.price_per_hour)))
            
            # Center align items
            for col in range(4):
                item = self.joy_table.item(i, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Actions - Fixed: using column index 4, not 5
            actions_widget = self._create_action_buttons(
                lambda checked, jid=joy.id: self.edit_joystick(jid),
                lambda checked, jid=joy.id: self.delete_joystick(jid)
            )
            self.joy_table.setCellWidget(i, 4, actions_widget)
    
    def load_users(self):
        """Load users into table"""
        users = AuthController.get_all_users()
        self.users_table.setRowCount(len(users))
        
        current_user = AuthController.get_current_user()
        
        for i, user in enumerate(users):
            # Set row height
            self.users_table.setRowHeight(i, 50)
            
            self.users_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(i, 1, QTableWidgetItem(user.full_name))
            self.users_table.setItem(i, 2, QTableWidgetItem(user.username))
            
            # Last login
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
            self.users_table.setItem(i, 3, QTableWidgetItem(last_login))
            
            # Center align items
            for col in range(4):
                item = self.users_table.item(i, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Actions - Don't allow deleting own account
            delete_callback = None
            if current_user and user.id != current_user.id:
                delete_callback = lambda checked, uid=user.id: self.delete_user(uid)
            
            actions_widget = self._create_action_buttons(
                lambda checked, uid=user.id: self.edit_user(uid),
                delete_callback
            )
            self.users_table.setCellWidget(i, 4, actions_widget)

    # ============== PLAYSTATION CRUD ==============
    
    def add_playstation(self):
        """Add new playstation"""
        dialog = AddEditDialog("Добавить PlayStation", [
            ("Имя", "text", ""),
            ("Модель", "combo", ["PS5", "PS4", "PS4 Pro", "PS3"]),
            ("Цена/час", "number", DEFAULT_PS_HOUR_PRICE)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Имя"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = PlaystationController.create_playstation(
                name=values["Имя"].strip(),
                model=values["Модель"],
                price_per_hour=values["Цена/час"]
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
            QMessageBox.warning(self, "Error", "Playstation не найден!")
            return
        
        dialog = AddEditDialog("Изменить PlayStation", [
            ("Имя", "text", ps.name),
            ("Модель", "combo", ["PS5", "PS4", "PS4 Pro", "PS3"], ps.model),
            ("Цена/час", "number", ps.price_per_hour)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Имя"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = PlaystationController.update_playstation(
                ps_id=ps_id,
                name=values["Имя"].strip(),
                model=values["Модель"],
                price_per_hour=values["Цена/час"]
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
            self, "Вы уверены?",
            f"Вы точно хотите удалить '{ps.name}'?\n\n Это действие нельзя будет отменить.",
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
        dialog = AddEditDialog("Добавить Джойстик", [
            ("Имя", "text", ""),
            ("Модель", "combo", ["DualSense", "DualShock 4", "DualShock 3"]),
            ("Цена/час", "number", DEFAULT_JOYSTICK_HOUR_PRICE)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Имя"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = JoystickController.create_joystick(
                name=values["Имя"].strip(),
                model=values["Модель"],
                price_per_hour=values["Цена/час"]
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
            QMessageBox.warning(self, "Error", "Joystick не найден!")
            return
        
        dialog = AddEditDialog("Изменить Джойстик", [
            ("Имя", "text", joystick.name),
            ("Модель", "combo", ["DualSense", "DualShock 4", "DualShock 3"], joystick.model),
            ("Цена/час", "number", joystick.price_per_hour)
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            if not values["Имя"].strip():
                QMessageBox.warning(self, "Error", "Name is required!")
                return
                
            success, message = JoystickController.update_joystick(
                joystick_id=joy_id,
                name=values["Имя"].strip(),
                model=values["Модель"],
                price_per_hour=values["Цена/час"]
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
            self, "Вы уверены?",
            f"Вы точно хотите удалить '{joystick.name}'?\n\n Это действие нельзя будет отменить.",
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
        dialog = AddEditDialog("Добавить Администратора", [
            ("Полное Имя", "text", ""),
            ("Имя Пользователя", "text", ""),
            ("Пароль", "password", "")
        ], self)
        
        if dialog.exec():
            values = dialog.get_values()
            
            # Validation
            if not values["Полное Имя"].strip():
                QMessageBox.warning(self, "Error", "Полное имя пользователя обязательно!")
                return
            if not values["Имя Пользователя"].strip():
                QMessageBox.warning(self, "Error", "Имя пользователя обязательно!")
                return
            if not values["Пароль"]:
                QMessageBox.warning(self, "Error", "Пароль обязателен!")
                return
            if len(values["Пароль"]) < 6:
                QMessageBox.warning(self, "Error", "Пароль должен содержать не менее 6 символов!")
                return
                
            success, message = AuthController.create_user(
                full_name=values["Полное Имя"].strip(),
                username=values["Имя Пользователя"].strip(),
                password=values["Пароль"]
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
            QMessageBox.warning(self, "Error", "Пользователь не найден!")
            return
        
        dialog = EditUserDialog(user, self)
        
        if dialog.exec():
            values = dialog.get_values()
            
            if not values["Полное Имя"].strip():
                QMessageBox.warning(self, "Error", "Полное имя пользователя обязательно!")
                return
            
            # Check if password should be updated
            new_password = values.get("Новый Пароль", "")
            if new_password and len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Пароль должен содержать не менее 6 символов!")
                return
                
            success, message = AuthController.update_user(
                user_id=user_id,
                full_name=values["Полное Имя"].strip(),
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
            QMessageBox.warning(self, "Error", "Ты не можешь удалить свой собственный аккаунт!")
            return
            
        reply = QMessageBox.question(
            self, "Вы уверены?",
            f"Вы точно хотите удалить '{user.full_name}'?\n\n Это действие нельзя будет отменить.",
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
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
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
        self.setWindowTitle(f"Обновить - {user.username}")
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
        title_label = QLabel(f"✏️ Обновить: {self.user.username}")
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
        form_layout.addRow("Полное имя:", self.full_name_input)
        self.fields["Полное Имя"] = self.full_name_input
        
        # Username (read-only)
        username_input = QLineEdit()
        username_input.setText(self.user.username)
        username_input.setReadOnly(True)
        username_input.setMinimumHeight(35)
        username_input.setStyleSheet("background-color: #e0e0e0;")
        form_layout.addRow("Имя пользователья:", username_input)
        
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
        
        password_title = QLabel("🔐 Изменить Пароль (Опционально)")
        password_title.setStyleSheet("font-weight: bold; border: none;")
        password_layout.addWidget(password_title)
        
        password_note = QLabel("Оставьте пустым, чтобы сохранить текущий пароль")
        password_note.setStyleSheet("color: gray; font-size: 12px; border: none;")
        password_layout.addWidget(password_note)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Новый пароль (минимум 6 символов)")
        self.new_password_input.setMinimumHeight(35)
        password_layout.addWidget(self.new_password_input)
        self.fields["Новый Пароль"] = self.new_password_input
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Подтвердить новый пароль")
        self.confirm_password_input.setMinimumHeight(35)
        password_layout.addWidget(self.confirm_password_input)
        
        layout.addWidget(password_group)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
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
                QMessageBox.warning(self, "Error", "Пароль и его подтверждение не совпадают!")
                return
            if len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Пароль должен содержать не менее 6 символов!")
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

