"""
Reports widget for generating and viewing reports
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QFrame,
    QDateEdit, QGroupBox, QGridLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

from controllers import ReportController
from utils import StyleManager, format_currency, format_duration


class ReportsWidget(QWidget):
    """Widget for report generation and viewing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Reports & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Report type tabs
        tabs = QTabWidget()
        
        # Daily tab
        daily_tab = QWidget()
        daily_layout = QVBoxLayout(daily_tab)
        
        daily_btn = QPushButton("📅 Generate Daily Report")
        daily_btn.clicked.connect(self.generate_daily_report)
        daily_layout.addWidget(daily_btn)
        
        tabs.addTab(daily_tab, "Daily")
        
        # Weekly tab
        weekly_tab = QWidget()
        weekly_layout = QVBoxLayout(weekly_tab)
        
        weekly_btn = QPushButton("📆 Generate Weekly Report")
        weekly_btn.clicked.connect(self.generate_weekly_report)
        weekly_layout.addWidget(weekly_btn)
        
        tabs.addTab(weekly_tab, "Weekly")
        
        # Monthly tab
        monthly_tab = QWidget()
        monthly_layout = QVBoxLayout(monthly_tab)
        
        monthly_btn = QPushButton("📅 Generate Monthly Report")
        monthly_btn.clicked.connect(self.generate_monthly_report)
        monthly_layout.addWidget(monthly_btn)
        
        tabs.addTab(monthly_tab, "Monthly")
        
        # Custom tab
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        custom_btn = QPushButton("Generate Custom Report")
        custom_btn.clicked.connect(self.generate_custom_report)
        date_layout.addWidget(custom_btn)
        
        date_layout.addStretch()
        custom_layout.addLayout(date_layout)
        
        tabs.addTab(custom_tab, "Custom")
        
        layout.addWidget(tabs)
        
        # Report display area
        self.report_frame = QFrame()
        self.report_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        report_layout = QVBoxLayout(self.report_frame)
        
        # Overview section
        overview_group = QGroupBox("📈 Overview")
        self.overview_grid = QGridLayout(overview_group)
        
        self.sessions_label = QLabel("Sessions: -")
        self.overview_grid.addWidget(self.sessions_label, 0, 0)
        
        self.revenue_label = QLabel("Revenue: -")
        self.overview_grid.addWidget(self.revenue_label, 0, 1)
        
        self.hours_label = QLabel("Total Hours: -")
        self.overview_grid.addWidget(self.hours_label, 0, 2)
        
        self.avg_session_label = QLabel("Avg Session: -")
        self.overview_grid.addWidget(self.avg_session_label, 1, 0)
        
        self.avg_revenue_label = QLabel("Avg Revenue: -")
        self.overview_grid.addWidget(self.avg_revenue_label, 1, 1)
        
        self.most_used_label = QLabel("Most Used: -")
        self.overview_grid.addWidget(self.most_used_label, 1, 2)
        
        report_layout.addWidget(overview_group)
        
        # Payment breakdown
        payment_group = QGroupBox("💳 Payment Breakdown")
        payment_layout = QHBoxLayout(payment_group)
        
        self.cash_label = QLabel("Cash: -")
        payment_layout.addWidget(self.cash_label)
        
        self.terminal_label = QLabel("Terminal: -")
        payment_layout.addWidget(self.terminal_label)
        
        self.hybrid_label = QLabel("Hybrid: -")
        payment_layout.addWidget(self.hybrid_label)
        
        payment_layout.addStretch()
        
        report_layout.addWidget(payment_group)
        
        # Playstation breakdown table
        ps_group = QGroupBox("🎮 Playstation Breakdown")
        ps_layout = QVBoxLayout(ps_group)
        
        self.ps_table = QTableWidget()
        self.ps_table.setColumnCount(4)
        self.ps_table.setHorizontalHeaderLabels(["Playstation", "Sessions", "Hours", "Revenue"])
        self.ps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ps_table.setAlternatingRowColors(True)
        ps_layout.addWidget(self.ps_table)
        
        report_layout.addWidget(ps_group)
        
        layout.addWidget(self.report_frame)
    
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
        self.sessions_label.setText(f"Sessions: {report['total_sessions']}")
        self.revenue_label.setText(f"Revenue: {format_currency(report['total_revenue'])}")
        self.hours_label.setText(f"Total Hours: {report['total_hours']:.1f}")
        self.avg_session_label.setText(f"Avg Duration: {format_duration(report['average_session_duration'])}")
        self.avg_revenue_label.setText(f"Avg Revenue: {format_currency(report['average_session_revenue'])}")
        self.most_used_label.setText(f"Most Used: {report['most_used_playstation'] or '-'}")
        
        # Update payment breakdown
        self.cash_label.setText(f"💵 Cash: {format_currency(report['cash_revenue'])} ({report['cash_sessions']} sessions)")
        self.terminal_label.setText(f"💳 Terminal: {format_currency(report['terminal_revenue'])} ({report['terminal_sessions']} sessions)")
        self.hybrid_label.setText(f"🔀 Hybrid: {report['hybrid_sessions']} sessions")
        
        # Update playstation table
        ps_revenue = report['revenue_per_playstation']
        ps_hours = report['hours_per_playstation']
        ps_sessions = report['sessions_per_playstation']
        
        self.ps_table.setRowCount(len(ps_revenue))
        
        for i, ps_name in enumerate(ps_revenue.keys()):
            self.ps_table.setItem(i, 0, QTableWidgetItem(ps_name))
            self.ps_table.setItem(i, 1, QTableWidgetItem(str(ps_sessions.get(ps_name, 0))))
            self.ps_table.setItem(i, 2, QTableWidgetItem(f"{ps_hours.get(ps_name, 0):.1f}"))
            self.ps_table.setItem(i, 3, QTableWidgetItem(format_currency(ps_revenue.get(ps_name, 0))))