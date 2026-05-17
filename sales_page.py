"""
Sales Page - صفحة المبيعات
Standalone page for sales management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem, QGroupBox
)
import sqlite3


class SalesPage(QWidget):
    """Standalone Sales Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_sales()
    
    def _setup_ui(self):
        """Setup Sales UI"""
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
        
        title = QLabel("💰 Sales Management — إدارة المبيعات")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Track sales, orders, and revenue — تتبع المبيعات والطلبات والإيرادات")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ New Sale — عملية بيع جديدة")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_sale)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_sales)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Sales Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "Sale #", "Client", "Date", "Amount (MAD)", "Status", "Payment", "Actions"
        ])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.sales_table)
        
        # Summary
        summary_group = QGroupBox("Sales Summary — ملخص المبيعات")
        summary_layout = QHBoxLayout()
        
        self.sales_total_label = QLabel("Total Sales: 0 MAD")
        self.sales_count_label = QLabel("Total Orders: 0")
        self.sales_pending_label = QLabel("Pending: 0 MAD")
        
        summary_layout.addWidget(self.sales_total_label)
        summary_layout.addWidget(self.sales_count_label)
        summary_layout.addWidget(self.sales_pending_label)
        summary_layout.addStretch()
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
    
    def _load_sales(self):
        """Load sales from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_number TEXT UNIQUE,
                    client_id INTEGER,
                    client_name TEXT,
                    sale_date TEXT,
                    total_amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT id, sale_number, client_name, sale_date, total_amount, status, payment_status FROM enterprise_sales ORDER BY id DESC")
            sales = cursor.fetchall()
            conn.close()
            
            self.sales_table.setRowCount(len(sales))
            total = 0
            pending = 0
            
            for row, sale in enumerate(sales):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale[1]) if sale[1] else ""))
                self.sales_table.setItem(row, 1, QTableWidgetItem(str(sale[2]) if sale[2] else ""))
                self.sales_table.setItem(row, 2, QTableWidgetItem(str(sale[3]) if sale[3] else ""))
                self.sales_table.setItem(row, 3, QTableWidgetItem(f"{sale[4]:.2f}" if sale[4] else "0.00"))
                self.sales_table.setItem(row, 4, QTableWidgetItem(str(sale[5]) if sale[5] else "pending"))
                self.sales_table.setItem(row, 5, QTableWidgetItem(str(sale[6]) if sale[6] else "pending"))
                
                total += sale[4] or 0
                if sale[6] == 'pending':
                    pending += sale[4] or 0
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, s_id=sale[0]: self._view_sale(s_id))
                self.sales_table.setCellWidget(row, 6, actions_btn)
            
            self.sales_total_label.setText(f"Total Sales: {total:.2f} MAD")
            self.sales_count_label.setText(f"Total Orders: {len(sales)}")
            self.sales_pending_label.setText(f"Pending: {pending:.2f} MAD")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading sales: {str(e)}")
    
    def _add_sale(self):
        """Add new sale"""
        QMessageBox.information(self, "Add Sale", "Sale creation feature will be implemented soon.")
    
    def _view_sale(self, sale_id: int):
        """View sale details"""
        QMessageBox.information(self, "Sale Details", f"Sale #{sale_id} details will be shown here.")
