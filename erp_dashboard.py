"""
Modern SaaS ERP Dashboard Module
Dark blue gradient theme with glassmorphism effects
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QGridLayout, QScrollArea, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPen, QIcon
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer, QPropertyAnimation, QEasingCurve
import math
from datetime import datetime, timedelta
import random

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class HexagonalIcon(QWidget):
    """Hexagonal brain icon for AI Assistant"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw hexagon
        center = QPoint(40, 40)
        radius = 30
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            points.append(QPoint(int(x), int(y)))
        
        # Fill with gradient
        gradient = QLinearGradient(0, 0, 80, 80)
        gradient.setColorAt(0, QColor(255, 165, 0, 200))
        gradient.setColorAt(1, QColor(255, 140, 0, 200))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 200, 100), 2))
        painter.drawPolygon(*points)
        
        # Draw brain pattern (simplified)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        # Neural network pattern
        for i in range(3):
            for j in range(3):
                x = 20 + i * 20
                y = 20 + j * 20
                painter.drawEllipse(x - 3, y - 3, 6, 6)
                if i < 2:
                    painter.drawLine(x, y, x + 20, y)
                if j < 2:
                    painter.drawLine(x, y, x, y + 20)


class GlassCard(QFrame):
    """Enhanced glassmorphism card with backdrop blur effect - Fintech style"""
    
    def __init__(self, parent=None, enhanced=True):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.enhanced = enhanced
        
        if enhanced:
            # Enhanced glassmorphism with better blur effect
            # Note: Qt doesn't support backdrop-filter, using enhanced transparency instead
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(51, 65, 85, 0.25);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 20px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(51, 65, 85, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                }
            """)
        
        # Enhanced shadow effect for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30 if enhanced else 20)
        shadow.setColor(QColor(0, 0, 0, 100 if enhanced else 80))
        shadow.setOffset(0, 6 if enhanced else 4)
        self.setGraphicsEffect(shadow)


class ChartWidget(QWidget):
    """Chart widget with gradient colors"""
    
    def __init__(self, chart_type="line", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.data = []
        self.labels = []
        
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(6, 3), facecolor='none')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: transparent;")
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.canvas)
            self.update_chart()
        else:
            # Fallback: simple painted chart
            self.setMinimumHeight(200)
    
    def set_data(self, data, labels=None):
        self.data = data
        self.labels = labels or ["Day {}".format(i+1) for i in range(len(data))]
        self.update_chart()
    
    def update_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            self.update()
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('rgba(255, 255, 255, 0.3)')
        ax.spines['left'].set_color('rgba(255, 255, 255, 0.3)')
        ax.tick_params(colors='rgba(255, 255, 255, 0.7)')
        ax.xaxis.label.set_color('rgba(255, 255, 255, 0.7)')
        ax.yaxis.label.set_color('rgba(255, 255, 255, 0.7)')
        
        if self.chart_type == "line":
            # Orange gradient line chart
            ax.plot(self.labels, self.data, color='#FF6B35', linewidth=3, marker='o', markersize=6)
            ax.fill_between(self.labels, self.data, alpha=0.3, color='#FF6B35')
        elif self.chart_type == "bar":
            # Teal gradient bar chart
            bars = ax.bar(self.labels, self.data, color='#20B2AA', alpha=0.8)
            for bar in bars:
                bar.set_edgecolor('#00CED1')
                bar.set_linewidth(1)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def paintEvent(self, event):
        if MATPLOTLIB_AVAILABLE:
            super().paintEvent(event)
            return
            
        # Fallback painted chart
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            return
            
        margin = 40
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        max_val = max(self.data) if self.data else 1
        
        # Draw grid
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        for i in range(5):
            y = int(margin + (height * i / 4))
            painter.drawLine(margin, y, margin + width, y)
        
        if self.chart_type == "line":
            # Draw line
            painter.setPen(QPen(QColor(255, 107, 53), 3))
            points = []
            for i, val in enumerate(self.data):
                x = margin + (width * i / (len(self.data) - 1)) if len(self.data) > 1 else margin + width / 2
                y = margin + height - (height * val / max_val)
                points.append(QPoint(int(x), int(y)))
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
                painter.setBrush(QBrush(QColor(255, 107, 53)))
                painter.drawEllipse(points[i], 4, 4)


class ERPDashboard(QWidget):
    """Modern SaaS ERP Dashboard with glassmorphism design"""
    
    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
        self.start_animations()
    
    def init_ui(self):
        """Initialize dashboard UI"""
        # Main layout with gradient background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(51, 65, 85, 0.3);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                min-height: 20px;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # AI Assistant Card
        ai_card = self.create_ai_assistant_card()
        content_layout.addWidget(ai_card)
        
        # Financial Analytics Widgets (Enhanced)
        analytics_row = self.create_analytics_widgets()
        content_layout.addWidget(analytics_row)
        
        # Additional Financial Metrics Row
        metrics_row = self.create_financial_metrics_row()
        content_layout.addWidget(metrics_row)
        
        # Charts Row (Enhanced with more charts)
        charts_row = self.create_charts_row()
        content_layout.addWidget(charts_row)
        
        # Revenue Breakdown Row
        revenue_row = self.create_revenue_breakdown_row()
        content_layout.addWidget(revenue_row)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Set background gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #334155);
            }
        """)
    
    def create_header(self):
        """Create dashboard header"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("AGAMART - Tableau de Bord")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # User info
        user_name = self.user.get('full_name') or self.user.get('username', 'Utilisateur')
        user_label = QLabel(f"👤 {user_name}")
        user_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 8px 16px;
                background-color: rgba(51, 65, 85, 0.4);
                border-radius: 8px;
            }
        """)
        header_layout.addWidget(user_label)
        
        return header_frame
    
    def create_ai_assistant_card(self):
        """Create AI Assistant card with hexagonal brain icon"""
        card = GlassCard()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 20, 30, 20)
        card_layout.setSpacing(20)
        
        # Hexagonal brain icon
        brain_icon = HexagonalIcon()
        card_layout.addWidget(brain_icon)
        
        # AI Assistant content
        ai_content = QVBoxLayout()
        ai_content.setSpacing(8)
        
        ai_title = QLabel("Assistant IA")
        ai_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        ai_content.addWidget(ai_title)
        
        ai_desc = QLabel("Analysez vos données, obtenez des insights et optimisez vos opérations avec l'intelligence artificielle.")
        ai_desc.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        ai_desc.setWordWrap(True)
        ai_content.addWidget(ai_desc)
        
        # Action button
        ai_button = QPushButton("Démarrer l'analyse")
        ai_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B35, stop:1 #FF8C42);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF8C42, stop:1 #FFA366);
            }
        """)
        ai_content.addWidget(ai_button)
        
        card_layout.addLayout(ai_content, 1)
        
        return card
    
    def create_analytics_widgets(self):
        """Create enhanced financial analytics widgets - Fintech style"""
        widgets_frame = QFrame()
        widgets_layout = QGridLayout(widgets_frame)
        widgets_layout.setSpacing(15)
        widgets_layout.setContentsMargins(0, 0, 0, 0)
        
        # Get data from database if available
        stock_value = self.get_stock_value()
        late_invoices = self.get_late_invoices_count()
        orders_count = self.get_orders_count()
        revenue = self.get_revenue()
        profit = self.get_profit()
        
        widgets = [
            ("💰", "Valeur du Stock", f"{stock_value:,.0f} DA", "#20B2AA", "+12.5%"),
            ("📄", "Factures en Retard", str(late_invoices), "#FF6B35", "-8.2%"),
            ("📦", "Commandes", str(orders_count), "#4A90E2", "+23.1%"),
            ("💵", "Revenus", f"{revenue:,.0f} DA", "#9B59B6", "+18.7%"),
        ]
        
        for i, widget_data in enumerate(widgets):
            if len(widget_data) == 5:
                icon, title, value, color, trend = widget_data
                widget = self.create_enhanced_analytics_widget(icon, title, value, color, trend)
            else:
                icon, title, value, color = widget_data
                widget = self.create_analytics_widget(icon, title, value, color)
            widgets_layout.addWidget(widget, 0, i)
        
        return widgets_frame
    
    def create_financial_metrics_row(self):
        """Create additional financial metrics row"""
        metrics_frame = QFrame()
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(15)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        
        profit = self.get_profit()
        cash_flow = self.get_cash_flow()
        growth = self.get_growth_rate()
        
        metrics = [
            ("📈", "Bénéfice Net", f"{profit:,.0f} DA", "#00C853", "+15.3%"),
            ("💸", "Flux de Trésorerie", f"{cash_flow:,.0f} DA", "#2196F3", "+9.8%"),
            ("🚀", "Croissance", f"{growth:.1f}%", "#FF9800", "+4.2%"),
        ]
        
        for i, (icon, title, value, color, trend) in enumerate(metrics):
            widget = self.create_enhanced_analytics_widget(icon, title, value, color, trend)
            metrics_layout.addWidget(widget, 0, i)
        
        return metrics_frame
    
    def create_analytics_widget(self, icon, title, value, color):
        """Create individual analytics widget"""
        card = GlassCard(enhanced=True)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        header_layout.addWidget(title_label)
        card_layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        card_layout.addWidget(value_label)
        
        return card
    
    def create_enhanced_analytics_widget(self, icon, title, value, color, trend):
        """Create enhanced analytics widget with trend indicator - Fintech style"""
        card = GlassCard(enhanced=True)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        header_layout.addWidget(title_label)
        card_layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        card_layout.addWidget(value_label)
        
        # Trend indicator
        trend_label = QLabel(trend)
        trend_color = "#00C853" if trend.startswith("+") else "#FF5252"
        trend_label.setStyleSheet(f"""
            QLabel {{
                color: {trend_color};
                font-size: 12px;
                font-weight: 600;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 4px 8px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }}
        """)
        card_layout.addWidget(trend_label)
        
        return card
    
    def create_charts_row(self):
        """Create enhanced charts row with multiple financial charts"""
        charts_frame = QFrame()
        charts_layout = QHBoxLayout(charts_frame)
        charts_layout.setSpacing(15)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        
        # Revenue chart (line with area fill)
        revenue_card = GlassCard(enhanced=True)
        revenue_layout = QVBoxLayout(revenue_card)
        revenue_layout.setContentsMargins(20, 20, 20, 20)
        
        revenue_title = QLabel("Revenus (30 derniers jours)")
        revenue_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin-bottom: 10px;
            }
        """)
        revenue_layout.addWidget(revenue_title)
        
        revenue_chart = ChartWidget("line")
        revenue_data = self.get_revenue_data()
        revenue_chart.set_data(revenue_data[0], revenue_data[1])
        revenue_chart.setMinimumHeight(280)
        revenue_layout.addWidget(revenue_chart)
        
        charts_layout.addWidget(revenue_card, 1)
        
        # Profit chart (area)
        profit_card = GlassCard(enhanced=True)
        profit_layout = QVBoxLayout(profit_card)
        profit_layout.setContentsMargins(20, 20, 20, 20)
        
        profit_title = QLabel("Bénéfices par Mois")
        profit_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin-bottom: 10px;
            }
        """)
        profit_layout.addWidget(profit_title)
        
        profit_chart = ChartWidget("bar")
        profit_data = self.get_profit_data()
        profit_chart.set_data(profit_data[0], profit_data[1])
        profit_chart.setMinimumHeight(280)
        profit_layout.addWidget(profit_chart)
        
        charts_layout.addWidget(profit_card, 1)
        
        return charts_frame
    
    def create_revenue_breakdown_row(self):
        """Create revenue breakdown chart row"""
        breakdown_frame = QFrame()
        breakdown_layout = QHBoxLayout(breakdown_frame)
        breakdown_layout.setSpacing(15)
        breakdown_layout.setContentsMargins(0, 0, 0, 0)
        
        # Revenue by category
        category_card = GlassCard(enhanced=True)
        category_layout = QVBoxLayout(category_card)
        category_layout.setContentsMargins(20, 20, 20, 20)
        
        category_title = QLabel("Répartition des Revenus par Catégorie")
        category_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin-bottom: 10px;
            }
        """)
        category_layout.addWidget(category_title)
        
        category_chart = ChartWidget("bar")
        category_data = self.get_orders_by_category()
        category_chart.set_data(category_data[0], category_data[1])
        category_chart.setMinimumHeight(250)
        category_layout.addWidget(category_chart)
        
        breakdown_layout.addWidget(category_card, 1)
        
        # Cash flow chart
        cashflow_card = GlassCard(enhanced=True)
        cashflow_layout = QVBoxLayout(cashflow_card)
        cashflow_layout.setContentsMargins(20, 20, 20, 20)
        
        cashflow_title = QLabel("Flux de Trésorerie")
        cashflow_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin-bottom: 10px;
            }
        """)
        cashflow_layout.addWidget(cashflow_title)
        
        cashflow_chart = ChartWidget("line")
        cashflow_data = self.get_cashflow_data()
        cashflow_chart.set_data(cashflow_data[0], cashflow_data[1])
        cashflow_chart.setMinimumHeight(250)
        cashflow_layout.addWidget(cashflow_chart)
        
        breakdown_layout.addWidget(cashflow_card, 1)
        
        return breakdown_frame
    
    def get_stock_value(self):
        """Get total stock value from database"""
        if not self.db:
            return 125000.0  # Mock data
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT SUM(price * stock_quantity) 
                FROM products 
                WHERE stock_quantity > 0
            """)
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 125000.0
        except:
            return 125000.0
    
    def get_late_invoices_count(self):
        """Get count of late invoices"""
        if not self.db:
            return 3  # Mock data
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM invoices 
                WHERE payment_status = 'pending' 
                AND due_date < date('now')
            """)
            result = cursor.fetchone()
            return result[0] if result else 3
        except:
            return 3
    
    def get_orders_count(self):
        """Get total orders count"""
        if not self.db:
            return 47  # Mock data
        
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM invoices")
            result = cursor.fetchone()
            return result[0] if result else 47
        except:
            return 47
    
    def get_sales_data(self):
        """Get sales data for last 7 days"""
        if not self.db:
            # Mock data
            days = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
            labels = [d.strftime("%d/%m") for d in days]
            values = [random.randint(50000, 150000) for _ in range(7)]
            return (values, labels)
        
        try:
            cursor = self.db.cursor()
            values = []
            labels = []
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM invoices
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                result = cursor.fetchone()
                values.append(float(result[0]) if result else 0)
                labels.append(date.strftime("%d/%m"))
            return (values, labels)
        except:
            days = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
            labels = [d.strftime("%d/%m") for d in days]
            values = [random.randint(50000, 150000) for _ in range(7)]
            return (values, labels)
    
    def get_orders_by_category(self):
        """Get orders grouped by category"""
        if not self.db:
            # Mock data
            categories = ["Électronique", "Vêtements", "Alimentaire", "Bureau"]
            values = [random.randint(10, 50) for _ in categories]
            return (values, categories)
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT p.category, COUNT(*) as count
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                GROUP BY p.category
                ORDER BY count DESC
                LIMIT 4
            """)
            results = cursor.fetchall()
            if results:
                values = [r[1] for r in results]
                labels = [r[0] or "Sans catégorie" for r in results]
                return (values, labels)
        except:
            pass
        
        # Fallback mock data
        categories = ["Électronique", "Vêtements", "Alimentaire", "Bureau"]
        values = [random.randint(10, 50) for _ in categories]
        return (values, categories)
    
    def get_revenue(self):
        """Get total revenue"""
        if not self.db:
            return 450000.0
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM invoices
                WHERE payment_status = 'paid'
            """)
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 450000.0
        except:
            return 450000.0
    
    def get_profit(self):
        """Get total profit"""
        revenue = self.get_revenue()
        # Estimate profit as 30% of revenue
        return revenue * 0.30
    
    def get_cash_flow(self):
        """Get cash flow"""
        if not self.db:
            return 320000.0
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM invoices
                WHERE payment_status = 'paid'
                AND DATE(created_at) >= DATE('now', '-30 days')
            """)
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 320000.0
        except:
            return 320000.0
    
    def get_growth_rate(self):
        """Get growth rate percentage"""
        return 12.5  # Mock data
    
    def get_revenue_data(self):
        """Get revenue data for last 30 days"""
        if not self.db:
            days = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
            labels = [d.strftime("%d/%m") for d in days[::3]]  # Every 3 days
            values = [random.randint(80000, 200000) for _ in range(10)]
            return (values, labels)
        
        try:
            cursor = self.db.cursor()
            values = []
            labels = []
            for i in range(29, -1, -3):  # Every 3 days
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM invoices
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                result = cursor.fetchone()
                values.append(float(result[0]) if result else random.randint(80000, 200000))
                labels.append(date.strftime("%d/%m"))
            return (values, labels)
        except:
            days = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
            labels = [d.strftime("%d/%m") for d in days[::3]]
            values = [random.randint(80000, 200000) for _ in range(10)]
            return (values, labels)
    
    def get_profit_data(self):
        """Get profit data by month"""
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
        values = [random.randint(50000, 150000) for _ in months]
        return (values, months)
    
    def get_cashflow_data(self):
        """Get cash flow data"""
        days = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime("%d/%m") for d in days]
        values = [random.randint(40000, 120000) for _ in range(7)]
        return (values, labels)
    
    def start_animations(self):
        """Start any UI animations"""
        # Could add fade-in animations here
        pass

