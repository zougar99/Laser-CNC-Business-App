"""
Invoices Page - صفحة الفواتير
Standalone page for invoices management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem
)
import sqlite3


class InvoicesPage(QWidget):
    """Standalone Invoices Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_invoices()
    
    def _setup_ui(self):
        """Setup Invoices UI"""
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
        
        title = QLabel("🧾 Invoices Management — إدارة الفواتير")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Manage all your invoices — إدارة جميع الفواتير")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Invoice — إضافة فاتورة")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_invoice)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_invoices)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Invoices Table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice #", "Client", "Date", "Amount (MAD)", "Status", "Due Date", "Actions"
        ])
        self.invoices_table.horizontalHeader().setStretchLastSection(True)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.invoices_table)
        
        layout.addStretch()
    
    def _load_invoices(self):
        """Load invoices from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE,
                    client_id INTEGER,
                    client_name TEXT,
                    issue_date TEXT,
                    due_date TEXT,
                    total_amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT id, invoice_number, client_name, issue_date, total_amount, status, due_date FROM enterprise_invoices ORDER BY id DESC")
            invoices = cursor.fetchall()
            conn.close()
            
            self.invoices_table.setRowCount(len(invoices))
            for row, invoice in enumerate(invoices):
                self.invoices_table.setItem(row, 0, QTableWidgetItem(str(invoice[1]) if invoice[1] else ""))
                self.invoices_table.setItem(row, 1, QTableWidgetItem(str(invoice[2]) if invoice[2] else ""))
                self.invoices_table.setItem(row, 2, QTableWidgetItem(str(invoice[3]) if invoice[3] else ""))
                self.invoices_table.setItem(row, 3, QTableWidgetItem(f"{invoice[4]:.2f}" if invoice[4] else "0.00"))
                self.invoices_table.setItem(row, 4, QTableWidgetItem(str(invoice[5]) if invoice[5] else "pending"))
                self.invoices_table.setItem(row, 5, QTableWidgetItem(str(invoice[6]) if invoice[6] else ""))
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, i_id=invoice[0]: self._view_invoice(i_id))
                self.invoices_table.setCellWidget(row, 6, actions_btn)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading invoices: {str(e)}")
    
    def _add_invoice(self):
        """Add new invoice"""
        QMessageBox.information(self, "Add Invoice", "Invoice creation feature will be implemented soon.")
    
    def _view_invoice(self, invoice_id: int):
        """View invoice details"""
        QMessageBox.information(self, "Invoice Details", f"Invoice #{invoice_id} details will be shown here.")
