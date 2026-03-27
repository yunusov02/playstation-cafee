from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QFrame,
    QDateEdit, QGroupBox, QGridLayout, QHeaderView, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

from controllers import ReportController
from utils import StyleManager, format_currency, format_duration


class ReportsWidget(QWidget):
    """
    Widget for report generation and viewing with full dark mode support
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report = None
        self.is_dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with title and export button
        header_layout = QHBoxLayout()
        
        # Title
        self.title = QLabel("📊 Отчеты и аналитика")
        self.title.setObjectName("reportTitle")
        header_layout.addWidget(self.title)
        
        header_layout.addStretch()
        
        # Export button
        self.export_btn = QPushButton("📥 Экспорт CSV")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.clicked.connect(self.export_report)
        header_layout.addWidget(self.export_btn)
        
        layout.addLayout(header_layout)
        
        # Report type tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("reportTabs")
        
        # Daily tab
        daily_tab = QWidget()
        daily_tab.setObjectName("tabContent")
        daily_layout = QVBoxLayout(daily_tab)
        daily_layout.setContentsMargins(15, 15, 15, 15)
        
        self.daily_btn = QPushButton("📅 Генерировать ежедневный отчет")
        self.daily_btn.setObjectName("generateBtn")
        self.daily_btn.setMinimumHeight(45)
        self.daily_btn.clicked.connect(self.generate_daily_report)
        daily_layout.addWidget(self.daily_btn)
        daily_layout.addStretch()
        
        self.tabs.addTab(daily_tab, "Ежедневный")
        
        # Weekly tab
        weekly_tab = QWidget()
        weekly_tab.setObjectName("tabContent")
        weekly_layout = QVBoxLayout(weekly_tab)
        weekly_layout.setContentsMargins(15, 15, 15, 15)
        
        self.weekly_btn = QPushButton("📆 Генерировать еженедельный отчет")
        self.weekly_btn.setObjectName("generateBtn")
        self.weekly_btn.setMinimumHeight(45)
        self.weekly_btn.clicked.connect(self.generate_weekly_report)
        weekly_layout.addWidget(self.weekly_btn)
        weekly_layout.addStretch()
        
        self.tabs.addTab(weekly_tab, "Еженедельный")
        
        # Monthly tab
        monthly_tab = QWidget()
        monthly_tab.setObjectName("tabContent")
        monthly_layout = QVBoxLayout(monthly_tab)
        monthly_layout.setContentsMargins(15, 15, 15, 15)
        
        self.monthly_btn = QPushButton("📅 Генерировать ежемесячный отчет")
        self.monthly_btn.setObjectName("generateBtn")
        self.monthly_btn.setMinimumHeight(45)
        self.monthly_btn.clicked.connect(self.generate_monthly_report)
        monthly_layout.addWidget(self.monthly_btn)
        monthly_layout.addStretch()
        
        self.tabs.addTab(monthly_tab, "Ежемесячный")
        
        # Custom tab
        custom_tab = QWidget()
        custom_tab.setObjectName("tabContent")
        custom_layout = QVBoxLayout(custom_tab)
        custom_layout.setContentsMargins(15, 15, 15, 15)
        
        date_layout = QHBoxLayout()
        
        self.start_label = QLabel("Старт:")
        self.start_label.setObjectName("dateLabel")
        date_layout.addWidget(self.start_label)
        
        self.start_date = QDateEdit()
        self.start_date.setObjectName("dateEdit")
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumHeight(40)
        date_layout.addWidget(self.start_date)
        
        self.end_label = QLabel("Окончание:")
        self.end_label.setObjectName("dateLabel")
        date_layout.addWidget(self.end_label)
        
        self.end_date = QDateEdit()
        self.end_date.setObjectName("dateEdit")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumHeight(40)
        date_layout.addWidget(self.end_date)
        
        self.custom_btn = QPushButton("📊 Генерировать отчет")
        self.custom_btn.setObjectName("generateBtn")
        self.custom_btn.setMinimumHeight(40)
        self.custom_btn.clicked.connect(self.generate_custom_report)
        date_layout.addWidget(self.custom_btn)
        
        date_layout.addStretch()
        custom_layout.addLayout(date_layout)
        custom_layout.addStretch()
        
        self.tabs.addTab(custom_tab, "Пользовательский")
        
        layout.addWidget(self.tabs)
        
        # Report display area
        self.report_frame = QFrame()
        self.report_frame.setObjectName("reportFrame")
        report_layout = QVBoxLayout(self.report_frame)
        report_layout.setSpacing(15)
        
        # Overview section
        self.overview_group = QGroupBox("📈 Обзор")
        self.overview_group.setObjectName("reportGroup")
        self.overview_grid = QGridLayout(self.overview_group)
        self.overview_grid.setSpacing(15)
        
        self.sessions_label = QLabel("Сессии: -")
        self.sessions_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.sessions_label, 0, 0)
        
        self.revenue_label = QLabel("Доход: -")
        self.revenue_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.revenue_label, 0, 1)
        
        self.hours_label = QLabel("Всего часов: -")
        self.hours_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.hours_label, 0, 2)
        
        self.avg_session_label = QLabel("Средняя сессия: -")
        self.avg_session_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.avg_session_label, 1, 0)
        
        self.avg_revenue_label = QLabel("Средний доход: -")
        self.avg_revenue_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.avg_revenue_label, 1, 1)
        
        self.most_used_label = QLabel("Наиболее используемый: -")
        self.most_used_label.setObjectName("statLabel")
        self.overview_grid.addWidget(self.most_used_label, 1, 2)
        
        report_layout.addWidget(self.overview_group)
        
        # Payment breakdown
        self.payment_group = QGroupBox("💳 Разбивка платежей")
        self.payment_group.setObjectName("reportGroup")
        payment_layout = QHBoxLayout(self.payment_group)
        payment_layout.setSpacing(20)

        self.cash_label = QLabel("💵 Наличные: -")
        self.cash_label.setObjectName("paymentLabel")
        payment_layout.addWidget(self.cash_label)

        self.terminal_label = QLabel("💳 Карта: -")
        self.terminal_label.setObjectName("paymentLabel")
        payment_layout.addWidget(self.terminal_label)

        self.hybrid_label = QLabel("🔀 Смешанная оплата: -")
        self.hybrid_label.setObjectName("paymentLabel")
        payment_layout.addWidget(self.hybrid_label)
        
        payment_layout.addStretch()
        
        report_layout.addWidget(self.payment_group)
        
        # Playstation breakdown table
        self.ps_group = QGroupBox("🎮 Разбивка PlayStation")
        self.ps_group.setObjectName("reportGroup")
        ps_layout = QVBoxLayout(self.ps_group)
        
        self.ps_table = QTableWidget()
        self.ps_table.setObjectName("reportTable")
        self.ps_table.setColumnCount(4)
        self.ps_table.setHorizontalHeaderLabels(["PlayStation", "Сессии", "Часы", "Доход"])
        self.ps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ps_table.setAlternatingRowColors(True)
        self.ps_table.verticalHeader().setVisible(False)
        self.ps_table.setMinimumHeight(200)
        ps_layout.addWidget(self.ps_table)
        
        report_layout.addWidget(self.ps_group)
        
        layout.addWidget(self.report_frame)
        
        # Apply initial styling
        self.apply_theme(False)
    
    def apply_theme(self, is_dark: bool):
        """Apply dark or light theme to all components"""
        self.is_dark_mode = is_dark
        
        # if is_dark:
        #     self.setStyleSheet(self.get_dark_stylesheet())
        # else:
        self.setStyleSheet(self.get_light_stylesheet())
    

    def get_light_stylesheet(self) -> str:
        """Get light mode stylesheet"""
        return """
            /* Main Widget */
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Title */
            QLabel#reportTitle {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
            
            /* Stat Labels */
            QLabel#statLabel {
                font-size: 14px;
                color: #444444;
                padding: 8px;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            
            /* Payment Labels */
            QLabel#paymentLabel {
                font-size: 14px;
                color: #444444;
                padding: 10px 15px;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            
            /* Date Labels */
            QLabel#dateLabel {
                font-size: 14px;
                color: #666666;
            }
            
            /* Tab Widget */
            QTabWidget#reportTabs::pane {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                background-color: #ffffff;
                top: -1px;
            }
            
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #666666;
                padding: 12px 24px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #333333;
                border-bottom: 2px solid #22b573;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #f0f0f0;
                color: #333333;
            }
            
            /* Tab Content */
            QWidget#tabContent {
                background-color: #ffffff;
            }
            
            /* Buttons */
            QPushButton#generateBtn {
                background-color: #22b573;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#generateBtn:hover {
                background-color: #28c97f;
            }
            
            QPushButton#generateBtn:pressed {
                background-color: #1a9e5c;
            }
            
            QPushButton#exportBtn {
                background-color: #4a4e69;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
            }
            
            QPushButton#exportBtn:hover {
                background-color: #5a5e79;
            }
            
            /* Date Edit */
            QDateEdit#dateEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            
            QDateEdit#dateEdit:focus {
                border-color: #22b573;
            }
            
            QDateEdit#dateEdit::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QDateEdit#dateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #666666;
            }
            
            /* Calendar popup */
            QCalendarWidget {
                background-color: #ffffff;
                color: #333333;
            }
            
            QCalendarWidget QToolButton {
                color: #333333;
                background-color: #f0f0f0;
                border-radius: 4px;
                padding: 5px;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: #e0e0e0;
            }
            
            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #333333;
            }
            
            QCalendarWidget QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #d0d0d0;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #22b573;
                selection-color: #ffffff;
            }
            
            /* Report Frame */
            QFrame#reportFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
            }
            
            /* Group Boxes */
            QGroupBox#reportGroup {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #fafafa;
            }
            
            QGroupBox#reportGroup::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #22b573;
            }
            
            /* Table Widget */
            QTableWidget#reportTable {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
            }
            
            QTableWidget#reportTable::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            QTableWidget#reportTable::item:selected {
                background-color: #e8f5e9;
                color: #333333;
            }
            
            QTableWidget#reportTable::item:alternate {
                background-color: #fafafa;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #22b573;
                font-weight: bold;
                font-size: 13px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background-color: #f5f5f5;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
    
    def generate_daily_report(self):
        """Generate daily report"""
        report = ReportController.get_daily_report()
        self.display_report(report)
    
    def generate_weekly_report(self):
        """Generate weekly report"""
        report = ReportController.get_weekly_report()
        self.display_report(report)
    
    def generate_monthly_report(self):
        """Generate monthly report"""
        report = ReportController.get_monthly_report()
        self.display_report(report)
    
    def generate_custom_report(self):
        """Generate custom date range report"""
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(end, datetime.max.time())
        
        report = ReportController.get_custom_report(start_dt, end_dt)
        self.display_report(report)
    
    def display_report(self, report: dict):
        """Display report data"""
        self.current_report = report
        
        # Update overview
        self.sessions_label.setText(f"📊 Сессии: {report['total_sessions']}")
        self.revenue_label.setText(f"💰 Доход: {format_currency(report['total_revenue'])}")
        self.hours_label.setText(f"⏱️ Общие часы: {report['total_hours']:.1f}")
        self.avg_session_label.setText(f"⌛ Средняя продолжительность: {format_duration(report['average_session_duration'])}")
        self.avg_revenue_label.setText(f"📈 Средний доход: {format_currency(report['average_session_revenue'])}")
        self.most_used_label.setText(f"🎮 Наиболее используемый: {report['most_used_playstation'] or '-'}")
        
        # Update payment breakdown
        self.cash_label.setText(f"💵 Наличные: {format_currency(report['cash_revenue'])} ({report['cash_sessions']} сессий)")
        self.terminal_label.setText(f"💳 Карта: {format_currency(report['terminal_revenue'])} ({report['terminal_sessions']} сессий)")
        self.hybrid_label.setText(f"🔀 Смешанная оплата: {report['hybrid_sessions']} сессий")
        
        # Update playstation table
        ps_revenue = report['revenue_per_playstation']
        ps_hours = report['hours_per_playstation']
        ps_sessions = report['sessions_per_playstation']
        
        self.ps_table.setRowCount(len(ps_revenue))
        
        for i, ps_name in enumerate(sorted(ps_revenue.keys())):
            # PlayStation name
            name_item = QTableWidgetItem(ps_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ps_table.setItem(i, 0, name_item)
            
            # Sessions
            sessions_item = QTableWidgetItem(str(ps_sessions.get(ps_name, 0)))
            sessions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ps_table.setItem(i, 1, sessions_item)
            
            # Hours
            hours_item = QTableWidgetItem(f"{ps_hours.get(ps_name, 0):.1f}")
            hours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ps_table.setItem(i, 2, hours_item)
            
            # Revenue
            revenue_item = QTableWidgetItem(format_currency(ps_revenue.get(ps_name, 0)))
            revenue_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ps_table.setItem(i, 3, revenue_item)
    
    def export_report(self):
        """Export current report to CSV"""
        if not self.current_report:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Сначала сгенерируйте отчет для экспорта."
            )
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Экспортировать отчет",
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                import csv
                
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow(["PlayStation Café - Отчет"])
                    writer.writerow([f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([])
                    
                    # Summary
                    writer.writerow(["=== ОБЗОР ==="])
                    writer.writerow(["Всего сессий", self.current_report['total_sessions']])
                    writer.writerow(["Общий доход", self.current_report['total_revenue']])
                    writer.writerow(["Всего часов", f"{self.current_report['total_hours']:.1f}"])
                    writer.writerow(["Средняя длительность (мин)", f"{self.current_report['average_session_duration']:.1f}"])
                    writer.writerow(["Средний доход", f"{self.current_report['average_session_revenue']:.0f}"])
                    writer.writerow(["Самый используемый PS", self.current_report['most_used_playstation'] or '-'])
                    writer.writerow([])
                    
                    # Payment breakdown
                    writer.writerow(["=== ПЛАТЕЖИ ==="])
                    writer.writerow(["Наличные", self.current_report['cash_revenue'], f"{self.current_report['cash_sessions']} сессий"])
                    writer.writerow(["Карта", self.current_report['terminal_revenue'], f"{self.current_report['terminal_sessions']} сессий"])
                    writer.writerow(["Смешанная оплата", "", f"{self.current_report['hybrid_sessions']} сессий"])
                    writer.writerow([])
                    
                    # PlayStation breakdown
                    writer.writerow(["=== ПО PLAYSTATION ==="])
                    writer.writerow(["PlayStation", "Сессии", "Часы", "Доход"])
                    
                    ps_revenue = self.current_report['revenue_per_playstation']
                    ps_hours = self.current_report['hours_per_playstation']
                    ps_sessions = self.current_report['sessions_per_playstation']
                    
                    for ps_name in sorted(ps_revenue.keys()):
                        writer.writerow([
                            ps_name,
                            ps_sessions.get(ps_name, 0),
                            f"{ps_hours.get(ps_name, 0):.1f}",
                            ps_revenue.get(ps_name, 0)
                        ])
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Отчет успешно экспортирован:\n{filename}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось экспортировать отчет:\n{str(e)}"
                )
    
    def refresh(self):
        """Refresh the current report if exists"""
        if self.current_report:
            # Re-generate based on current tab
            current_tab = self.tabs.currentIndex()
            if current_tab == 0:
                self.generate_daily_report()
            elif current_tab == 1:
                self.generate_weekly_report()
            elif current_tab == 2:
                self.generate_monthly_report()
            elif current_tab == 3:
                self.generate_custom_report()

        