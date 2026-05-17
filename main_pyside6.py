"""
Main entry point for LaserFlow Application (PySide6)
Smart Laser Workshop Manager with Professional Theme

REQUIRES PYTHON 3.8+ - يتطلب Python 3.8 أو أحدث
Use: py -3 main_pyside6.py  or  python3 main_pyside6.py
"""

import sys

# Check Python version - التحقق من إصدار Python
if sys.version_info < (3, 8):
    print("=" * 60)
    print("ERROR: Python 3.8 or higher is required!")
    print("خطأ: يتطلب Python 3.8 أو أحدث")
    print("=" * 60)
    print(f"Current version: {sys.version}")
    print("Please use: py -3 main_pyside6.py  or  python3 main_pyside6.py")
    print("أو استخدم: run_app.bat")
    print("=" * 60)
    sys.exit(1)

from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt

from ui.router import AppRouter
from core.theme_manager import ThemeManager
try:
    from core.notifications import NotificationManager
except ImportError:
    NotificationManager = None


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Load version from config for window title
        import json
        from pathlib import Path
        config_path = Path("app_config.json")
        app_version = "1.0.0"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    app_version = config.get("app_version", "1.0.0")
            except:
                pass
        
        self.setWindowTitle(f"LaserFlow - Smart Laser Workshop Manager v{app_version}")
        self.setMinimumSize(1366, 768)
        
        # Set window icon (check for dev icon first, then production)
        from PySide6.QtGui import QIcon
        icon_path = Path(__file__).parent / "app_icon_dev.ico"
        if not icon_path.exists():
            icon_path = Path(__file__).parent / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize notification manager
        if NotificationManager:
            try:
                self.notification_manager = NotificationManager()
                # Show welcome notification
                from PySide6.QtCore import QTimer
                QTimer.singleShot(1000, lambda: self.notification_manager.add_notification(
                    "Welcome to LaserFlow!",
                    "Your smart laser workshop manager is ready.",
                    "success",
                    3000
                ))
            except:
                self.notification_manager = None
        else:
            self.notification_manager = None
        
        # Load QSS theme
        self._load_theme()
        
        # Setup UI
        self._setup_ui()
        
        # Update theme button icon after UI is ready
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._update_dashboard_theme_button)
        
        # Center window
        self._center_window()
    
    def _load_theme(self):
        """Load QSS theme file"""
        try:
            theme_content = self.theme_manager.load_theme()
            
            if theme_content:
                self.setStyleSheet(theme_content)
            else:
                print("Warning: Could not load theme")
        except Exception as e:
            print(f"Error loading theme: {e}")
            import traceback
            traceback.print_exc()
            # Use minimal fallback theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f4f8;
                    color: #2c3e50;
                    font-family: "Segoe UI", "Arial", sans-serif;
                }
            """)
    
    def _update_dashboard_theme_button(self):
        """Update theme button icon in dashboard"""
        dashboard = self.router.get_page("dashboard")
        if dashboard and hasattr(dashboard, 'theme_btn'):
            if self.theme_manager.is_dark():
                dashboard.theme_btn.setText("🌙")
                dashboard.theme_btn.setToolTip("Switch to Light Mode — المظهر الفاتح")
            else:
                dashboard.theme_btn.setText("☀️")
                dashboard.theme_btn.setToolTip("Switch to Dark Mode — المظهر الداكن")
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        new_mode = self.theme_manager.toggle_theme()
        self._load_theme()
        self._update_dashboard_theme_button()
        return new_mode
    
    def _setup_ui(self):
        """Setup main UI with Sidebar + Content"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout (horizontal: Sidebar + Content)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        try:
            from ui.components.sidebar import Sidebar
            self.sidebar = Sidebar()
            self.sidebar.page_requested.connect(self._on_sidebar_navigation)
            layout.addWidget(self.sidebar)
        except:
            self.sidebar = None
        
        # Content area (Top Bar + Router + ScrollArea)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top Bar
        try:
            from ui.components.top_bar import TopBar
            self.top_bar = TopBar()
            self.top_bar.search_requested.connect(self._on_search)
            self.top_bar.page_requested.connect(self._on_top_bar_navigation)
            content_layout.addWidget(self.top_bar)
        except:
            self.top_bar = None
        
        # Router (QStackedWidget - handles page navigation)
        notification_mgr = getattr(self, 'notification_manager', None)
        try:
            self.router = AppRouter(notification_manager=notification_mgr)
            self.router.page_changed.connect(self._on_page_changed)
            self.router.theme_toggle_requested.connect(self.toggle_theme)
        except Exception as e:
            print(f"Error creating AppRouter: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # CRITICAL: Wrap QStackedWidget in QScrollArea for proper scrolling
        scroll_area = QScrollArea()
        
        # CRITICAL: Must be True for scrolling to work!
        scroll_area.setWidgetResizable(True)
        
        # No frame for cleaner look
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setFrameShadow(QScrollArea.Plain)
        
        # Scroll bars - show when needed
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Smooth scrolling
        scroll_area.verticalScrollBar().setSingleStep(20)
        
        # Set router (QStackedWidget) as widget in scroll area
        scroll_area.setWidget(self.router)
        
        # CRITICAL: Ensure scroll area expands to fill available space
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # CRITICAL: Ensure QStackedWidget can grow beyond viewport
        self.router.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.router.setMinimumSize(0, 0)
        
        # After setting widget, update geometry
        scroll_area.updateGeometry()
        
        # Add scroll area to content layout
        content_layout.addWidget(scroll_area)
        
        # Add content widget to main layout
        layout.addWidget(content_widget, 1)
        
        # Store references
        self.scroll_area = scroll_area
    
    def _on_sidebar_navigation(self, page_id: str):
        """Handle sidebar navigation"""
        if self.router:
            self.router.navigate_to(page_id)
            # Update sidebar active state
            if self.sidebar:
                self.sidebar.set_active_page(page_id)
    
    def _on_top_bar_navigation(self, page_id: str):
        """Handle navigation from top bar"""
        if self.router:
            self.router.navigate_to(page_id)
    
    def _on_search(self, query: str):
        """Handle search from top bar"""
        # Forward search to current page if it supports it
        current_page = self.router.currentWidget()
        if current_page and hasattr(current_page, 'handle_search'):
            current_page.handle_search(query)
    
    def _center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def _on_page_changed(self, page_name: str):
        """Handle page change"""
        # Load version from config
        import json
        from pathlib import Path
        config_path = Path("app_config.json")
        app_version = "1.0.0"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    app_version = config.get("app_version", "1.0.0")
            except:
                pass
        
        # Update window title if needed
        page_titles = {
            "dashboard": "Dashboard",
            "add_job": "Add Laser Job",
            "client_approval": "Client Approval",
            "cost_awareness": "Cost Awareness",
            "jobs": "Laser Jobs",
            "business_legal": "Business & Legal",
            "enterprise_tools": "Enterprise Tools",
            "monthly_analysis": "Monthly Analysis",
            "job_details": "Job Details",
            "reports": "Reports & Analytics",
            "settings": "Settings",
            "notifications": "Notifications",
            "point_of_sale": "Point of Sale",
        }
        title = page_titles.get(page_name, "LaserFlow")
        self.setWindowTitle(f"LaserFlow - {title} v{app_version}")


def main():
    """Main entry point"""
    import json
    from pathlib import Path
    import logging
    
    # CRITICAL: Install Qt message handler BEFORE creating QApplication
    # This must be done before any Qt objects are created
    from PySide6.QtCore import qInstallMessageHandler, QtMsgType
    def qt_message_handler(msg_type, context, message):
        # Suppress QFont::setPointSize warnings
        message_str = str(message)
        if 'QFont::setPointSize' in message_str or 'Point size <= 0' in message_str or 'must be greater than 0' in message_str:
            # Log to debug file instead of console
            try:
                import json
                from datetime import datetime
                log_path = r"c:\Users\werlist99\Desktop\laser_pc_project11\.cursor\debug.log"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"timestamp": datetime.now().isoformat(), "location": "main_pyside6.py:qt_message_handler", "message": "QFont::setPointSize warning suppressed", "data": {"qt_message": message_str, "msg_type": str(msg_type), "file": str(context.file) if hasattr(context, 'file') else "", "line": str(context.line) if hasattr(context, 'line') else ""}, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "F"}) + "\n")
            except:
                pass
            return  # Suppress these warnings
        # Log other messages normally
        if msg_type >= QtMsgType.QtWarningMsg:
            print(f"Qt Warning: {message}")
    
    qInstallMessageHandler(qt_message_handler)
    
    # Suppress Qt font warnings by setting up logging filter
    # This prevents QFont::setPointSize warnings from cluttering the console
    class QtFontWarningFilter(logging.Filter):
        def filter(self, record):
            # Filter out QFont::setPointSize warnings
            if 'QFont::setPointSize' in str(record.getMessage()):
                return False
            return True
    
    # Configure logging to suppress Qt font warnings
    logging.basicConfig(level=logging.WARNING)
    qt_logger = logging.getLogger('PySide6')
    qt_logger.addFilter(QtFontWarningFilter())
    
    # Load version from config
    config_path = Path("app_config.json")
    app_version = "1.0.0"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                app_version = config.get("app_version", "1.0.0")
        except:
            pass
    
    app = QApplication(sys.argv)
    app.setApplicationName("LaserFlow")
    app.setApplicationVersion(app_version)
    
    # Set application icon
    from PySide6.QtGui import QIcon
    icon_path = Path("app_icon_dev.ico")
    if not icon_path.exists():
        icon_path = Path("app_icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.resize(1920, 1080)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
