"""
Clients Page - صفحة العملاء
Standalone page for client management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem
)
import sqlite3


class ClientsPage(QWidget):
    """Standalone Clients Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_clients()
    
    def _setup_ui(self):
        """Setup Clients UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        home_btn = QPushButton("🏠 Home")
        home_btn.setObjectName("Secondary")
        home_btn.setFixedHeight(40)
        home_btn.setFixedWidth(100)
        home_btn.clicked.connect(lambda: self.action_requested.emit("dashboard"))
        header_layout.addWidget(home_btn)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        title = QLabel("👥 Clients Management — إدارة العملاء")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Manage all your clients and customers — إدارة جميع العملاء والعملاء")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Client — إضافة عميل")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_client)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_clients)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Clients Table
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(7)
        self.clients_table.setHorizontalHeaderLabels([
            "Code", "Company/Name", "Contact", "Phone", "Email", "City", "Actions"
        ])
        self.clients_table.horizontalHeader().setStretchLastSection(True)
        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.clients_table)
        
        layout.addStretch()
    
    def _load_clients(self):
        """Load clients from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_code TEXT UNIQUE,
                    company_name TEXT,
                    contact_name TEXT,
                    phone TEXT,
                    email TEXT,
                    city TEXT,
                    address TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT id, client_code, company_name, contact_name, phone, email, city FROM enterprise_clients ORDER BY id DESC")
            clients = cursor.fetchall()
            conn.close()
            
            self.clients_table.setRowCount(len(clients))
            for row, client in enumerate(clients):
                for col, value in enumerate(client[1:], 0):  # Skip id
                    self.clients_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, c_id=client[0]: self._view_client(c_id))
                self.clients_table.setCellWidget(row, 6, actions_btn)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading clients: {str(e)}")
    
    def _add_client(self):
        """Add new client"""
        QMessageBox.information(self, "Add Client", "Client creation feature will be implemented soon.")
    
    def _view_client(self, client_id: int):
        """View client details"""
        QMessageBox.information(self, "Client Details", f"Client #{client_id} details will be shown here.")
