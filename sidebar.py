"""
Sidebar Component - LaserFlow
Professional sidebar navigation like LOGEC
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont


class Sidebar(QFrame):
    """Professional sidebar navigation"""
    
    page_requested = Signal(str)  # Emits page_id when clicked
    
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(0)  # Hide sidebar by setting width to 0
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.hide()  # Hide the sidebar completely
        self._setup_ui()
        self._current_page = "dashboard"
    
    def _setup_ui(self):
        """Setup sidebar UI - Empty sidebar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Empty sidebar - all navigation moved to Enterprise Tools
        self.buttons = {}
        
        # Just a spacer to fill the space
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def _on_button_clicked(self, page_id: str):
        """Handle sidebar button click"""
        # Update button states
        for pid, btn in self.buttons.items():
            btn.setChecked(pid == page_id)
        
        self._current_page = page_id
        self.page_requested.emit(page_id)
    
    def set_active_page(self, page_id: str):
        """Set active page from external source"""
        for pid, btn in self.buttons.items():
            btn.setChecked(pid == page_id)
        self._current_page = page_id
