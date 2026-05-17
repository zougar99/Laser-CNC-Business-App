"""
Production CNC Application - تطبيق إنتاج CNC/ليزر
All CNC/Laser machine and production related tools
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QSizePolicy, QSpacerItem, QTabWidget
)

from pathlib import Path
import json
import sqlite3


class ProductionCNCPage(QWidget):
    """Production CNC - All Machine & Production Tools"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup Production CNC UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = self._create_page_header("⚙️ Production CNC/Laser — إنتاج CNC/ليزر")
        layout.addWidget(header)
        
        # Info
        info = QLabel(
            "Complete CNC/Laser Production System — نظام إنتاج CNC/ليزر الكامل\n"
            "All tools for machine control, production, quality, and CNC/Laser operations"
        )
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Production Tools Grid
        tools_grid = QGridLayout()
        tools_grid.setSpacing(20)
        
        # === MACHINE CONTROL ===
        machine_group = QGroupBox("⚙️ Machine Control — تحكم الآلة")
        machine_layout = QVBoxLayout()
        machine_tools = [
            ("⚙️ Machine Control", self._open_machine_control),
            ("🔧 Machine Settings", self._open_machine_settings),
            ("📊 Machine Status", self._open_machine_status),
            ("🔄 Machine Maintenance", self._open_machine_maintenance),
        ]
        for tool_name, tool_func in machine_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            machine_layout.addWidget(btn)
        machine_group.setLayout(machine_layout)
        tools_grid.addWidget(machine_group, 0, 0)
        
        # === PRODUCTION QUEUE ===
        production_group = QGroupBox("🔧 Production Queue — قائمة الإنتاج")
        production_layout = QVBoxLayout()
        production_tools = [
            ("🔧 Production Queue", self._open_production_queue),
            ("📋 Job Management", self._open_job_management),
            ("⏱️ Time Tracking", self._open_time_tracking),
            ("📊 Production Reports", self._open_production_reports),
        ]
        for tool_name, tool_func in production_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            production_layout.addWidget(btn)
        production_group.setLayout(production_layout)
        tools_grid.addWidget(production_group, 0, 1)
        
        # === MATERIAL MANAGEMENT ===
        material_group = QGroupBox("🔩 Material Management — إدارة المواد")
        material_layout = QVBoxLayout()
        material_tools = [
            ("🔩 Material Management", self._open_material_management),
            ("📦 Material Stock", self._open_material_stock),
            ("📏 Material Calculator", self._open_material_calculator),
            ("💰 Material Costs", self._open_material_costs),
        ]
        for tool_name, tool_func in material_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            material_layout.addWidget(btn)
        material_group.setLayout(material_layout)
        tools_grid.addWidget(material_group, 1, 0)
        
        # === QUALITY CONTROL ===
        quality_group = QGroupBox("✅ Quality Control — فحص الجودة")
        quality_layout = QVBoxLayout()
        quality_tools = [
            ("✅ Quality Control", self._open_quality_control),
            ("📊 Quality Reports", self._open_quality_reports),
            ("🔍 Inspection", self._open_inspection),
            ("📈 Quality Metrics", self._open_quality_metrics),
        ]
        for tool_name, tool_func in quality_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            quality_layout.addWidget(btn)
        quality_group.setLayout(quality_layout)
        tools_grid.addWidget(quality_group, 1, 1)
        
        # === CNC/LASER SETTINGS ===
        settings_group = QGroupBox("⚙️ CNC/Laser Settings — إعدادات CNC/ليزر")
        settings_layout = QVBoxLayout()
        settings_tools = [
            ("⚙️ Machine Settings", self._open_cnc_settings),
            ("📐 Cutting Parameters", self._open_cutting_params),
            ("🎨 Design Files", self._open_design_files),
            ("📊 Performance", self._open_performance),
        ]
        for tool_name, tool_func in settings_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            settings_layout.addWidget(btn)
        settings_group.setLayout(settings_layout)
        tools_grid.addWidget(settings_group, 2, 0)
        
        # === ADVANCED TOOLS ===
        advanced_group = QGroupBox("🛠️ Advanced Production Tools — أدوات الإنتاج المتقدمة")
        advanced_layout = QVBoxLayout()
        advanced_tools = [
            ("🤖 AI Assistant", self._open_ai_assistant),
            ("📊 Production Analytics", self._open_production_analytics),
            ("🔔 Production Alerts", self._open_production_alerts),
            ("⚙️ Advanced Settings", self._open_advanced_settings),
        ]
        for tool_name, tool_func in advanced_tools:
            btn = QPushButton(tool_name)
            btn.setObjectName("Primary")
            btn.clicked.connect(tool_func)
            advanced_layout.addWidget(btn)
        advanced_group.setLayout(advanced_layout)
        tools_grid.addWidget(advanced_group, 2, 1)
        
        layout.addLayout(tools_grid)
        layout.addStretch()
    
    def _create_page_header(self, title: str) -> QWidget:
        """Create page header"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 16)
        header_layout.setSpacing(16)
        
        home_btn = QPushButton("🏠 Home")
        home_btn.setObjectName("Secondary")
        home_btn.setFixedHeight(40)
        home_btn.setFixedWidth(100)
        home_btn.clicked.connect(lambda: self.action_requested.emit("dashboard"))
        header_layout.addWidget(home_btn)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        title_label.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title_label)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        return header
    
    # Navigation methods
    def _open_machine_control(self):
        self.action_requested.emit("production_cnc")
    
    def _open_machine_settings(self):
        self.action_requested.emit("production_cnc")
    
    def _open_machine_status(self):
        self.action_requested.emit("production_cnc")
    
    def _open_machine_maintenance(self):
        self.action_requested.emit("production_cnc")
    
    def _open_production_queue(self):
        self.action_requested.emit("production_cnc")
    
    def _open_job_management(self):
        self.action_requested.emit("production_cnc")
    
    def _open_time_tracking(self):
        self.action_requested.emit("production_cnc")
    
    def _open_production_reports(self):
        self.action_requested.emit("production_cnc")
    
    def _open_material_management(self):
        self.action_requested.emit("production_cnc")
    
    def _open_material_stock(self):
        self.action_requested.emit("production_cnc")
    
    def _open_material_calculator(self):
        self.action_requested.emit("production_cnc")
    
    def _open_material_costs(self):
        self.action_requested.emit("production_cnc")
    
    def _open_quality_control(self):
        self.action_requested.emit("production_cnc")
    
    def _open_quality_reports(self):
        self.action_requested.emit("production_cnc")
    
    def _open_inspection(self):
        self.action_requested.emit("production_cnc")
    
    def _open_quality_metrics(self):
        self.action_requested.emit("production_cnc")
    
    def _open_cnc_settings(self):
        self.action_requested.emit("production_cnc")
    
    def _open_cutting_params(self):
        self.action_requested.emit("production_cnc")
    
    def _open_design_files(self):
        self.action_requested.emit("production_cnc")
    
    def _open_performance(self):
        self.action_requested.emit("production_cnc")
    
    def _open_ai_assistant(self):
        self.action_requested.emit("production_cnc")
    
    def _open_production_analytics(self):
        self.action_requested.emit("production_cnc")
    
    def _open_production_alerts(self):
        self.action_requested.emit("production_cnc")
    
    def _open_advanced_settings(self):
        self.action_requested.emit("production_cnc")
