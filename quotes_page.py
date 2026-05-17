"""
Quotes Page - صفحة العروض
Standalone page for quotes management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem
)
import sqlite3


class QuotesPage(QWidget):
    """Standalone Quotes Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_quotes()
    
    def _setup_ui(self):
        """Setup Quotes UI"""
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
        
        title = QLabel("📝 Quotes Management — إدارة العروض")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Manage all your quotes and price offers — إدارة جميع العروض وعروض الأسعار")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Quote — إضافة عرض")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_quote)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_quotes)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Quotes Table
        self.quotes_table = QTableWidget()
        self.quotes_table.setColumnCount(7)
        self.quotes_table.setHorizontalHeaderLabels([
            "Quote #", "Client", "Date", "Amount (MAD)", "Status", "Valid Until", "Actions"
        ])
        self.quotes_table.horizontalHeader().setStretchLastSection(True)
        self.quotes_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.quotes_table)
        
        layout.addStretch()
    
    def _load_quotes(self):
        """Load quotes from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_number TEXT UNIQUE,
                    client_id INTEGER,
                    client_name TEXT,
                    issue_date TEXT,
                    valid_until TEXT,
                    total_amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT id, quote_number, client_name, issue_date, total_amount, status, valid_until FROM enterprise_quotes ORDER BY id DESC")
            quotes = cursor.fetchall()
            conn.close()
            
            self.quotes_table.setRowCount(len(quotes))
            for row, quote in enumerate(quotes):
                self.quotes_table.setItem(row, 0, QTableWidgetItem(str(quote[1]) if quote[1] else ""))
                self.quotes_table.setItem(row, 1, QTableWidgetItem(str(quote[2]) if quote[2] else ""))
                self.quotes_table.setItem(row, 2, QTableWidgetItem(str(quote[3]) if quote[3] else ""))
                self.quotes_table.setItem(row, 3, QTableWidgetItem(f"{quote[4]:.2f}" if quote[4] else "0.00"))
                self.quotes_table.setItem(row, 4, QTableWidgetItem(str(quote[5]) if quote[5] else "pending"))
                self.quotes_table.setItem(row, 5, QTableWidgetItem(str(quote[6]) if quote[6] else ""))
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, q_id=quote[0]: self._view_quote(q_id))
                self.quotes_table.setCellWidget(row, 6, actions_btn)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading quotes: {str(e)}")
    
    def _add_quote(self):
        """Add new quote"""
        QMessageBox.information(self, "Add Quote", "Quote creation feature will be implemented soon.")
    
    def _view_quote(self, quote_id: int):
        """View quote details"""
        QMessageBox.information(self, "Quote Details", f"Quote #{quote_id} details will be shown here.")
