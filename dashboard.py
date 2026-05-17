"""
Dashboard Page - Professional CNC/Laser Workshop Manager
Main dashboard with CNC/Laser workflow and metrics
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QSizePolicy, QSpacerItem, QGroupBox, QGridLayout
)

from pathlib import Path
import json
import sqlite3


class DashboardPage(QWidget):
    """Professional Dashboard for CNC/Laser Workshop"""
    
    action_requested = Signal(str)
    theme_toggle_requested = Signal()
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_metrics()
    
    def _setup_ui(self):
        """Setup professional dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("⚡ CNC/Laser Workshop Manager — مدير ورشة CNC/ليزر")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 24px; font-weight: 600; color: #1F2937;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Theme toggle button
        self.theme_btn = QToolButton()
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setText("🌙")
        self.theme_btn.setToolTip("Toggle Theme — تبديل المظهر")
        self.theme_btn.clicked.connect(lambda: self.theme_toggle_requested.emit())
        header_layout.addWidget(self.theme_btn)
        
        layout.addLayout(header_layout)
        
        # Application Selection - اختيار التطبيق
        app_selection_group = QGroupBox("🚀 Choose Application — اختر التطبيق")
        app_selection_layout = QHBoxLayout()
        app_selection_layout.setSpacing(24)
        
        # Bureau Management App
        bureau_card = QGroupBox("💼 Bureau Management — إدارة المكتب")
        bureau_layout = QVBoxLayout()
        bureau_info = QLabel(
            "Complete Office & Management System\n"
            "نظام إدارة المكتب الكامل\n\n"
            "• Clients & Orders\n"
            "• Stock & Inventory\n"
            "• Sales & Finance\n"
            "• Shipping & Delivery\n"
            "• Reports & Settings"
        )
        bureau_info.setWordWrap(True)
        bureau_info.setObjectName("InfoLabel")
        bureau_layout.addWidget(bureau_info)
        
        bureau_btn = QPushButton("🚀 Open Bureau Management\nفتح إدارة المكتب")
        bureau_btn.setObjectName("Primary")
        bureau_btn.setMinimumHeight(80)
        bureau_btn.setStyleSheet("font-size: 16px; font-weight: 600; padding: 16px;")
        bureau_btn.clicked.connect(lambda: self.action_requested.emit("bureau_management"))
        bureau_layout.addWidget(bureau_btn)
        
        bureau_card.setLayout(bureau_layout)
        app_selection_layout.addWidget(bureau_card)
        
        # Production CNC App
        production_card = QGroupBox("⚙️ Production CNC/Laser — إنتاج CNC/ليزر")
        production_layout = QVBoxLayout()
        production_info = QLabel(
            "Complete CNC/Laser Production System\n"
            "نظام إنتاج CNC/ليزر الكامل\n\n"
            "• Machine Control\n"
            "• Production Queue\n"
            "• Material Management\n"
            "• Quality Control\n"
            "• CNC/Laser Settings"
        )
        production_info.setWordWrap(True)
        production_info.setObjectName("InfoLabel")
        production_layout.addWidget(production_info)
        
        production_btn = QPushButton("🚀 Open Production CNC\nفتح إنتاج CNC")
        production_btn.setObjectName("Primary")
        production_btn.setMinimumHeight(80)
        production_btn.setStyleSheet("font-size: 16px; font-weight: 600; padding: 16px;")
        production_btn.clicked.connect(lambda: self.action_requested.emit("production_cnc"))
        production_layout.addWidget(production_btn)
        
        production_card.setLayout(production_layout)
        app_selection_layout.addWidget(production_card)
        
        app_selection_group.setLayout(app_selection_layout)
        layout.addWidget(app_selection_group)
        
        # Key Metrics - المؤشرات الرئيسية
        metrics_group = QGroupBox("📊 Key Metrics — المؤشرات الرئيسية")
        metrics_group.setObjectName("MetricsGroup")
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(24)  # More spacing for clean look
        
        # Revenue Card
        revenue_card = QGroupBox("💰 Total Revenue — إجمالي الإيرادات")
        revenue_layout = QVBoxLayout()
        self.revenue_label = QLabel("0.00 MAD")
        self.revenue_label.setObjectName("MetricValue")
        self.revenue_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #16A34A;")
        revenue_layout.addWidget(self.revenue_label)
        revenue_card.setLayout(revenue_layout)
        metrics_layout.addWidget(revenue_card, 0, 0)
        
        # Jobs Card
        jobs_card = QGroupBox("⚙️ Active Jobs — الوظائف النشطة")
        jobs_layout = QVBoxLayout()
        self.jobs_label = QLabel("0")
        self.jobs_label.setObjectName("MetricValue")
        self.jobs_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #2563EB;")
        jobs_layout.addWidget(self.jobs_label)
        jobs_card.setLayout(jobs_layout)
        metrics_layout.addWidget(jobs_card, 0, 1)
        
        # Clients Card
        clients_card = QGroupBox("👥 Total Clients — إجمالي العملاء")
        clients_layout = QVBoxLayout()
        self.clients_label = QLabel("0")
        self.clients_label.setObjectName("MetricValue")
        self.clients_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #0EA5E9;")
        clients_layout.addWidget(self.clients_label)
        clients_card.setLayout(clients_layout)
        metrics_layout.addWidget(clients_card, 0, 2)
        
        # Pending Orders Card
        pending_card = QGroupBox("⏳ Pending Orders — الطلبات المعلقة")
        pending_layout = QVBoxLayout()
        self.pending_label = QLabel("0")
        self.pending_label.setObjectName("MetricValue")
        self.pending_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #F59E0B;")
        pending_layout.addWidget(self.pending_label)
        pending_card.setLayout(pending_layout)
        metrics_layout.addWidget(pending_card, 0, 3)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        layout.addStretch()
    
    def _load_metrics(self):
        """Load dashboard metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total Revenue
            cursor.execute("SELECT SUM(total_amount) FROM enterprise_sales")
            revenue = cursor.fetchone()[0] or 0
            self.revenue_label.setText(f"{revenue:.2f} MAD")
            
            # Active Jobs (sales in progress)
            cursor.execute("SELECT COUNT(*) FROM enterprise_sales WHERE status != 'completed'")
            jobs = cursor.fetchone()[0] or 0
            self.jobs_label.setText(str(jobs))
            
            # Total Clients
            cursor.execute("SELECT COUNT(*) FROM enterprise_clients")
            clients = cursor.fetchone()[0] or 0
            self.clients_label.setText(str(clients))
            
            # Pending Orders (quotes pending approval)
            cursor.execute("SELECT COUNT(*) FROM enterprise_quotes WHERE status = 'pending'")
            pending = cursor.fetchone()[0] or 0
            self.pending_label.setText(str(pending))
            
            conn.close()
        except Exception as e:
            # If tables don't exist yet, show zeros
            pass
