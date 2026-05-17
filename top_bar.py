"""
Top Bar Component - LaserFlow
Professional top bar like LOGEC ERP
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QIcon


class TopBar(QFrame):
    """Professional top bar with search and user info"""
    
    search_requested = Signal(str)  # Emits search query
    
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(56)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup top bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)
        
        # App Name / Logo
        app_label = QLabel("LaserFlow")
        app_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #1F2937;
        """)
        layout.addWidget(app_label)
        
        # Company Name (optional)
        company_label = QLabel("Company Name")
        company_label.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
        """)
        layout.addWidget(company_label)
        
        layout.addSpacing(16)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search... (Ctrl+F)")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMaximumWidth(400)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍")
        search_btn.setObjectName("Secondary")
        search_btn.setFixedSize(36, 36)
        search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # User Info
        user_label = QLabel("👤 User")
        user_label.setStyleSheet("""
            font-size: 14px;
            color: #1F2937;
            padding: 8px 12px;
            background-color: #F3F4F6;
            border-radius: 6px;
        """)
        layout.addWidget(user_label)
        
        # Settings Button
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("Secondary")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setToolTip("Settings")
        layout.addWidget(settings_btn)
    
    def _on_search(self):
        """Handle search"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
