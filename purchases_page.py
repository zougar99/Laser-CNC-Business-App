"""
Purchases Page - صفحة المشتريات
Standalone page for purchases management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem, QGroupBox
)
import sqlite3


class PurchasesPage(QWidget):
    """Standalone Purchases Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_purchases()
    
    def _setup_ui(self):
        """Setup Purchases UI"""
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
        
        title = QLabel("🛒 Purchases Management — إدارة المشتريات")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Track purchases, suppliers, and expenses — تتبع المشتريات والموردين والمصروفات")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Purchase — إضافة شراء")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_purchase)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_purchases)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Purchases Table
        self.purchases_table = QTableWidget()
        self.purchases_table.setColumnCount(7)
        self.purchases_table.setHorizontalHeaderLabels([
            "Purchase #", "Supplier", "Date", "Amount (MAD)", "Status", "Category", "Actions"
        ])
        self.purchases_table.horizontalHeader().setStretchLastSection(True)
        self.purchases_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.purchases_table)
        
        # Summary
        summary_group = QGroupBox("Purchases Summary — ملخص المشتريات")
        summary_layout = QHBoxLayout()
        
        self.purchases_total_label = QLabel("Total: 0 MAD")
        self.purchases_paid_label = QLabel("Paid: 0 MAD")
        self.purchases_pending_label = QLabel("Pending: 0 MAD")
        
        summary_layout.addWidget(self.purchases_total_label)
        summary_layout.addWidget(self.purchases_paid_label)
        summary_layout.addWidget(self.purchases_pending_label)
        summary_layout.addStretch()
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
    
    def _load_purchases(self):
        """Load purchases from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_number TEXT UNIQUE,
                    supplier_name TEXT,
                    purchase_date TEXT,
                    amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    category TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT id, purchase_number, supplier_name, purchase_date, amount, status, category FROM enterprise_purchases ORDER BY id DESC")
            purchases = cursor.fetchall()
            conn.close()
            
            self.purchases_table.setRowCount(len(purchases))
            total = 0
            paid = 0
            pending = 0
            
            for row, purchase in enumerate(purchases):
                self.purchases_table.setItem(row, 0, QTableWidgetItem(str(purchase[1]) if purchase[1] else ""))
                self.purchases_table.setItem(row, 1, QTableWidgetItem(str(purchase[2]) if purchase[2] else ""))
                self.purchases_table.setItem(row, 2, QTableWidgetItem(str(purchase[3]) if purchase[3] else ""))
                self.purchases_table.setItem(row, 3, QTableWidgetItem(f"{purchase[4]:.2f}" if purchase[4] else "0.00"))
                self.purchases_table.setItem(row, 4, QTableWidgetItem(str(purchase[5]) if purchase[5] else "pending"))
                self.purchases_table.setItem(row, 5, QTableWidgetItem(str(purchase[6]) if purchase[6] else ""))
                
                total += purchase[4] or 0
                if purchase[5] == 'paid':
                    paid += purchase[4] or 0
                else:
                    pending += purchase[4] or 0
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, p_id=purchase[0]: self._view_purchase(p_id))
                self.purchases_table.setCellWidget(row, 6, actions_btn)
            
            self.purchases_total_label.setText(f"Total: {total:.2f} MAD")
            self.purchases_paid_label.setText(f"Paid: {paid:.2f} MAD")
            self.purchases_pending_label.setText(f"Pending: {pending:.2f} MAD")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading purchases: {str(e)}")
    
    def _add_purchase(self):
        """Add new purchase"""
        QMessageBox.information(self, "Add Purchase", "Purchase creation feature will be implemented soon.")
    
    def _view_purchase(self, purchase_id: int):
        """View purchase details"""
        QMessageBox.information(self, "Purchase Details", f"Purchase #{purchase_id} details will be shown here.")
