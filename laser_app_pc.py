# -*- coding: utf-8 -*-
"""
Laser Job Manager (prototype)

This module contains a small Tkinter application to manage laser engraving
projects, store them in SQLite, and provide a handful of raster-prep utilities.
The goal of this refactor is to keep the original behavior while adding light
type hints, clarifying comments, and a few guardrails for a more maintainable
codebase.
"""

import math
import os
import shutil
import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional, Tuple

# محاولة استيراد مكتبة الصور (Pillow) لأدوات الفكتور
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

DB_NAME = "laser_app.db"
STATUS_NEW = "NEW"
BRAND_PRIMARY = "#2563EB"
BRAND_ACCENT = "#14B8A6"

# ============================================================================
# LANGUAGE SYSTEM - Multi-language support (AR/FR/EN)
# ============================================================================

class LanguageManager:
    """Manages application translations."""
    
    LANGUAGES = ["fr", "en", "ar"]
    
    TRANSLATIONS = {
        "ar": {
            "dashboard": "لوحة التحكم",
            "projects": "المشاريع",
            "new_project": "مشروع جديد",
            "vector_center": "مركز الفكتور",
            "modules": "الموديولات",
            "settings": "الإعدادات",
            "language": "اللغة",
            "current_job": "المشروع الحالي",
            "today_jobs": "مشاريع اليوم",
            "revenue": "الإيرادات",
            "notes": "ملاحظات",
            "today": "اليوم",
            "week": "الأسبوع",
            "no_active_job": "لا يوجد مشروع نشط",
            "no_today_jobs": "لا توجد مشاريع اليوم",
            "save": "حفظ",
            "search": "بحث",
            "refresh": "تحديث",
            "delete": "حذف",
            "back": "رجوع",
            "open_vector": "فتح في Vector Center",
            "open_project": "فتح المشروع",
            "project_name": "اسم المشروع",
            "customer": "الزبون",
            "customer_name": "اسم الزبون",
            "customer_phone": "هاتف الزبون",
            "price": "الثمن",
            "material": "المادة",
            "size": "المقاس",
            "status": "الحالة",
            "created_at": "تاريخ الإنشاء",
            "image": "الصورة",
            "phone": "الهاتف",
            "optional": "اختياري",
            "save_project": "حفظ المشروع",
            "toggle": "تفعيل / تعطيل",
            "machine_center": "مركز الآلة",
            "tools": "الأدوات",
            "yes": "نعم",
            "no": "لا",
            "backup_db": "نسخ قاعدة البيانات",
            "unit_converter": "محول الوحدات",
            "engraving_calc": "حساب وقت النقش",
            "quick_links": "روابط سريعة",
            "confirm_delete": "واش متأكد بغيتي تحذف؟",
            "select_job": "اختر مشروعاً.",
            "select_module": "اختر موديولاً.",
            "save_notes": "حفظ الملاحظات",
            "notes_saved_later": "سيتم حفظ الملاحظات في المستقبل.",
            "exit": "خروج",
            "exit_confirm": "واش بغيتي تخرج من البرنامج؟",
            "my_studio": "استوديوي",
            "lang_note": "التغييرات تطبق مباشرة.",
            "theme": "المظهر",
            "light": "فاتح",
            "dark": "داكن",
            "appearance": "المظهر",
        },
        "fr": {
            "dashboard": "Tableau de bord",
            "projects": "Projets",
            "new_project": "Nouveau projet",
            "vector_center": "Centre Vectoriel",
            "modules": "Modules",
            "settings": "Paramètres",
            "language": "Langue",
            "current_job": "Projet actuel",
            "today_jobs": "Projets d'aujourd'hui",
            "revenue": "Revenus",
            "notes": "Notes",
            "today": "Aujourd'hui",
            "week": "Semaine",
            "no_active_job": "Aucun projet actif",
            "no_today_jobs": "Aucun projet aujourd'hui",
            "save": "Enregistrer",
            "search": "Rechercher",
            "refresh": "Actualiser",
            "delete": "Supprimer",
            "back": "Retour",
            "open_vector": "Ouvrir dans Vector Center",
            "open_project": "Ouvrir le projet",
            "project_name": "Nom du projet",
            "customer": "Client",
            "customer_name": "Nom du client",
            "customer_phone": "Téléphone du client",
            "price": "Prix",
            "material": "Matière",
            "size": "Taille",
            "status": "Statut",
            "created_at": "Date de création",
            "image": "Image",
            "phone": "Téléphone",
            "optional": "Optionnel",
            "save_project": "Enregistrer le projet",
            "toggle": "Activer / Désactiver",
            "machine_center": "Centre Machine",
            "tools": "Outils",
            "yes": "Oui",
            "no": "Non",
            "backup_db": "Sauvegarder la base",
            "unit_converter": "Convertisseur d'unités",
            "engraving_calc": "Temps de gravure",
            "quick_links": "Liens rapides",
            "confirm_delete": "Êtes-vous sûr de vouloir supprimer ?",
            "select_job": "Sélectionnez un projet.",
            "select_module": "Sélectionnez un module.",
            "save_notes": "Enregistrer les notes",
            "notes_saved_later": "Les notes seront enregistrées plus tard.",
            "exit": "Quitter",
            "exit_confirm": "Voulez-vous quitter l'application ?",
            "my_studio": "Mon Studio",
            "lang_note": "Les changements de langue s'appliquent immédiatement.",
            "theme": "Thème",
            "light": "Clair",
            "dark": "Sombre",
            "appearance": "Apparence",
        },
        "en": {
            "dashboard": "Dashboard",
            "projects": "Projects",
            "new_project": "New Project",
            "vector_center": "Vector Center",
            "modules": "Modules",
            "settings": "Settings",
            "language": "Language",
            "current_job": "Current Job",
            "today_jobs": "Today's Jobs",
            "revenue": "Revenue",
            "notes": "Notes",
            "today": "Today",
            "week": "Week",
            "no_active_job": "No active job",
            "no_today_jobs": "No jobs today",
            "save": "Save",
            "search": "Search",
            "refresh": "Refresh",
            "delete": "Delete",
            "back": "Back",
            "open_vector": "Open in Vector Center",
            "open_project": "Open Project",
            "project_name": "Project Name",
            "customer": "Customer",
            "customer_name": "Customer Name",
            "customer_phone": "Customer Phone",
            "price": "Price",
            "material": "Material",
            "size": "Size",
            "status": "Status",
            "created_at": "Created At",
            "image": "Image",
            "phone": "Phone",
            "optional": "Optional",
            "save_project": "Save Project",
            "toggle": "Toggle",
            "machine_center": "Machine Center",
            "tools": "Tools",
            "yes": "Yes",
            "no": "No",
            "backup_db": "Backup database",
            "unit_converter": "Unit Converter",
            "engraving_calc": "Engraving Time",
            "quick_links": "Quick Links",
            "confirm_delete": "Are you sure you want to delete?",
            "select_job": "Select a job.",
            "select_module": "Select a module.",
            "save_notes": "Save Notes",
            "notes_saved_later": "Notes will be saved in the future.",
            "exit": "Exit",
            "exit_confirm": "Do you want to exit the application?",
            "my_studio": "My Studio",
            "lang_note": "Language changes apply immediately.",
            "theme": "Theme",
            "light": "Light",
            "dark": "Dark",
            "appearance": "Appearance",
        },
    }
    
    def __init__(self, default_lang: str = "ar"):
        self.current_lang = default_lang if default_lang in self.LANGUAGES else "ar"
    
    def get(self, key: str, default: str = "") -> str:
        """Get translation for a key."""
        return self.TRANSLATIONS.get(self.current_lang, {}).get(key, default or key)
    
    def set_language(self, lang: str) -> None:
        """Set current language."""
        if lang in self.LANGUAGES:
            self.current_lang = lang
    
    def get_language(self) -> str:
        """Get current language code."""
        return self.current_lang

# ============================================================================
# UI ENGINE - Professional Theme & Style System
# ============================================================================

class UIEngine:
    """Professional UI Engine for theme, layout, and style management."""
    
    # Theme definitions
    THEMES = {
        "light": {
            "bg": "#FFFFFF",
            "surface": "#F8FAFC",
            "primary": "#3B82F6",
            "text": "#111827",
            "muted": "#6B7280",
            "border": "#E5E7EB",
            "heading_bg": "#E5F0FF",
            "sidebar_bg": "#0F172A",
            "sidebar_text": "#F9FAFB",
            "sidebar_active": "#22D3EE",
            "sidebar_hover": "#1E293B",
        },
        "dark": {
            "bg": "#0C111D",
            "surface": "#1F2937",
            "primary": "#22D3EE",
            "text": "#F9FAFB",
            "muted": "#94A3B8",
            "border": "#334155",
            "heading_bg": "#1E293B",
            "sidebar_bg": "#020617",
            "sidebar_text": "#E2E8F0",
            "sidebar_active": "#22D3EE",
            "sidebar_hover": "#0F172A",
        },
        "industrial": {
            "bg": "#0B1220",
            "surface": "#111827",
            "primary": BRAND_PRIMARY,
            "text": "#E5E7EB",
            "muted": "#9CA3AF",
            "border": "#1F2937",
            "heading_bg": "#0F172A",
            "sidebar_bg": "#030712",
            "sidebar_text": "#D1D5DB",
            "sidebar_active": BRAND_ACCENT,
            "sidebar_hover": "#111827",
        },
        "erp_pro": {
            "bg": "#F3F6FB",
            "surface": "#FFFFFF",
            "primary": BRAND_PRIMARY,
            "text": "#0F172A",
            "muted": "#475569",
            "border": "#D9E2F1",
            "heading_bg": "#EAF1FC",
            "sidebar_bg": "#0F172A",
            "sidebar_text": "#E2E8F0",
            "sidebar_active": BRAND_ACCENT,
            "sidebar_hover": "#1E293B",
        },
    }
    
    # Layout modes
    LAYOUT_SIDEBAR = "sidebar"
    LAYOUT_TOPBAR = "topbar"
    LAYOUT_BOTH = "both"
    
    # UI styles
    STYLE_MODERN = "modern"
    STYLE_FLUTTER = "flutter"
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(root)
        self.current_theme = "light"
        self.current_layout = self.LAYOUT_BOTH
        self.current_ui_style = self.STYLE_MODERN
        self._init_style()
    
    def _init_style(self) -> None:
        """Initialize base ttk style."""
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
    
    def get_theme(self) -> dict:
        """Get current theme colors."""
        return self.THEMES[self.current_theme]
    
    def set_theme(self, theme_name: str) -> None:
        """Change theme (light/dark)."""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self._apply_theme()
    
    def set_layout(self, layout: str) -> None:
        """Set layout mode (sidebar/topbar/both)."""
        self.current_layout = layout
    
    def set_ui_style(self, style: str) -> None:
        """Set UI style (modern/flutter)."""
        self.current_ui_style = style
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply current theme to all widgets."""
        colors = self.get_theme()
        # Compact profile by default for dense desktop workflows.
        base_font = ("Segoe UI", 9)
        heading_font = ("Segoe UI", 14, "bold")
        button_font = ("Segoe UI", 10, "bold")
        
        # Base elements
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("Card.TFrame", background=colors["surface"], padding=10)
        self.style.configure("Panel.TFrame", background=colors["surface"], padding=8)
        self.style.configure("HeaderBar.TFrame", background=colors["heading_bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["text"], font=base_font)
        self.style.configure("Heading.TLabel", background=colors["bg"], foreground=colors["text"], font=heading_font)
        self.style.configure("HeaderTitle.TLabel", background=colors["heading_bg"], foreground=colors["text"], font=("Segoe UI", 12, "bold"))
        self.style.configure("HeaderMeta.TLabel", background=colors["heading_bg"], foreground=colors["muted"], font=("Segoe UI", 9))
        self.style.configure("Subtle.TLabel", background=colors["bg"], foreground=colors["muted"], font=base_font)
        
        # Sidebar styles
        self.style.configure("Sidebar.TFrame", background=colors["sidebar_bg"])
        self.style.configure("Sidebar.TLabel", background=colors["sidebar_bg"], foreground=colors["sidebar_text"])
        self.style.configure("Sidebar.TButton", 
            background=colors["sidebar_bg"],
            foreground=colors["sidebar_text"],
            font=("Segoe UI", 10),
            padding=(12, 8),
            anchor="w",
            borderwidth=0,
        )
        self.style.map("Sidebar.TButton",
            background=[("active", colors["sidebar_hover"]), ("selected", colors["sidebar_hover"])],
        )
        
        # Buttons
        self.style.configure("Primary.TButton",
            background=colors["primary"],
            foreground="#FFFFFF",
            padding=(10, 7),
            font=button_font,
            borderwidth=0,
        )
        self.style.map("Primary.TButton",
            background=[("active", self._darken(colors["primary"])), ("pressed", self._darken(colors["primary"], 0.2))],
        )
        
        self.style.configure("Outline.TButton",
            background=colors["bg"],
            foreground=colors["primary"],
            padding=(10, 7),
            font=button_font,
            relief="solid",
            borderwidth=1,
        )
        self.style.map("Outline.TButton",
            background=[("active", colors["surface"]), ("pressed", colors["border"])],
        )
        
        # Entry / Combobox
        self.style.configure("TEntry",
            fieldbackground=colors["surface"],
            foreground=colors["text"],
            insertcolor=colors["text"],
            padding=6,
            borderwidth=1,
            relief="solid",
        )
        self.style.configure("TCombobox",
            fieldbackground=colors["surface"],
            foreground=colors["text"],
            padding=4,
            borderwidth=1,
            relief="solid",
        )
        
        # Treeview - theme-aware alternating rows
        self.style.configure("App.Treeview",
            background=colors["surface"],
            fieldbackground=colors["surface"],
            foreground=colors["text"],
            rowheight=28,
            borderwidth=0,
        )
        self.style.configure("App.Treeview.Heading",
            background=colors["heading_bg"],
            foreground=colors["text"],
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=6,
        )
        self.style.map("App.Treeview",
            background=[("selected", colors["primary"] + "50")],
            foreground=[("selected", colors["text"])],
        )
        # Alternating row colors for Treeview - theme-aware
        self._tree_even_bg = colors["surface"]
        self._tree_odd_bg = colors["bg"] if colors["bg"] != colors["surface"] else self._lighten(colors["surface"], 0.03)
        
        # Update root background
        self.root.configure(bg=colors["bg"])

        # Top tabs navigation styles
        self.style.configure(
            "TopTabs.TFrame",
            background=colors["heading_bg"],
        )
        self.style.configure(
            "TabNav.TButton",
            background=colors["heading_bg"],
            foreground=colors["text"],
            borderwidth=1,
            relief="solid",
            padding=(12, 5),
            font=("Segoe UI", 9, "bold"),
        )
        self.style.map(
            "TabNav.TButton",
            foreground=[("active", colors["primary"]), ("selected", colors["primary"])],
            background=[("active", colors["surface"]), ("selected", colors["surface"])],
            bordercolor=[("active", colors["primary"]), ("selected", colors["primary"])],
        )

    def get_tree_row_colors(self) -> Tuple[str, str]:
        """Get alternating row colors for Treeview."""
        return (getattr(self, "_tree_even_bg", "#FFFFFF"), getattr(self, "_tree_odd_bg", "#F9FAFB"))
    
    def _darken(self, hex_color: str, factor: float = 0.15) -> str:
        """Darken a hex color."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lighten(self, hex_color: str, factor: float = 0.1) -> str:
        """Lighten a hex color."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"


# Legacy constants for backward compatibility
COLOR_BG = "#FFFFFF"
COLOR_SURFACE = "#F8FAFC"
COLOR_PRIMARY = "#3B82F6"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_HEADING_BG = "#E5F0FF"


def apply_app_theme(root: tk.Tk, ui_engine: Optional[UIEngine] = None) -> ttk.Style:
    """Configure theme - uses UIEngine if provided, otherwise legacy."""
    if ui_engine:
        return ui_engine.style
    # Legacy fallback
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    return style


class LaserDB:
    """Minimal SQLite wrapper for jobs and modules tables."""

    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image_path TEXT,
                customer_name TEXT,
                customer_phone TEXT,
                price REAL,
                notes TEXT,
                plate_width REAL,
                plate_height REAL,
                material_type TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                version TEXT NOT NULL,
                installed INTEGER NOT NULL
            )
            """
        )
        self.conn.commit()
        self._seed_modules()

    def _seed_modules(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM modules")
        (count,) = cur.fetchone()
        if count == 0:
            modules = [
                ("vectorizer_v1", "Vectorizer v1", "Basic vectorization tool (placeholder)", "1.0.0", 1),
                ("templates_basic", "Basic Templates", "Simple shapes and frames", "1.0.0", 1),
                ("ai_remote", "Remote AI", "Use server AI (future)", "0.0.1", 0),
            ]
            cur.executemany(
                "INSERT INTO modules (id, name, description, version, installed) VALUES (?, ?, ?, ?, ?)",
                modules,
            )
            self.conn.commit()

    # Jobs
    def create_job(
        self,
        name: str,
        image_path: str,
        customer_name: str,
        customer_phone: str,
        price: Optional[float],
        notes: str,
        plate_width: Optional[float],
        plate_height: Optional[float],
        material_type: str,
    ) -> int:
        cur = self.conn.cursor()
        created_at = datetime.now().isoformat(timespec="seconds")
        status = STATUS_NEW
        cur.execute(
            """
            INSERT INTO jobs
            (
                name, image_path, customer_name, customer_phone, price,
                notes, plate_width, plate_height, material_type,
                created_at, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                image_path,
                customer_name,
                customer_phone,
                price,
                notes,
                plate_width,
                plate_height,
                material_type,
                created_at,
                status,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_jobs(self, search_text: Optional[str] = None) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        if search_text:
            like = f"%{search_text}%"
            cur.execute(
                """
                SELECT id, name, customer_name, customer_phone,
                       price, material_type, plate_width, plate_height,
                       image_path, created_at, status
                FROM jobs
                WHERE name LIKE ? OR customer_name LIKE ?
                ORDER BY created_at DESC
                """,
                (like, like),
            )
        else:
            cur.execute(
                """
                SELECT id, name, customer_name, customer_phone,
                       price, material_type, plate_width, plate_height,
                       image_path, created_at, status
                FROM jobs
                ORDER BY created_at DESC
                """
            )
        return list(cur.fetchall())

    def get_job(self, job_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, name, customer_name, customer_phone,
                   price, material_type, plate_width, plate_height,
                   image_path, created_at, status, notes
            FROM jobs
            WHERE id = ?
            """,
            (job_id,),
        )
        return cur.fetchone()

    def delete_job(self, job_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        self.conn.commit()

    # Dashboard helpers
    def get_current_job(self) -> Optional[sqlite3.Row]:
        """Get the latest active job (status != DONE)."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, name, customer_name, customer_phone,
                   price, material_type, plate_width, plate_height,
                   image_path, created_at, status, notes
            FROM jobs
            WHERE status != 'DONE'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
        return cur.fetchone()

    def get_today_jobs(self) -> List[sqlite3.Row]:
        """Get jobs created today."""
        cur = self.conn.cursor()
        today = datetime.now().date().isoformat()
        cur.execute(
            """
            SELECT id, name, customer_name, price, status, created_at
            FROM jobs
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC
            """,
            (today,),
        )
        return list(cur.fetchall())

    def get_today_revenue(self) -> float:
        """Calculate total revenue from today's jobs."""
        cur = self.conn.cursor()
        today = datetime.now().date().isoformat()
        cur.execute(
            """
            SELECT COALESCE(SUM(price), 0) as total
            FROM jobs
            WHERE DATE(created_at) = ? AND price IS NOT NULL
            """,
            (today,),
        )
        result = cur.fetchone()
        return float(result["total"]) if result else 0.0

    def get_week_revenue(self) -> float:
        """Calculate total revenue from this week."""
        cur = self.conn.cursor()
        # Get start of week (Monday)
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        cur.execute(
            """
            SELECT COALESCE(SUM(price), 0) as total
            FROM jobs
            WHERE DATE(created_at) >= ? AND price IS NOT NULL
            """,
            (week_start.isoformat(),),
        )
        result = cur.fetchone()
        return float(result["total"]) if result else 0.0

    def get_jobs_summary(self) -> dict:
        """Get summary stats: total, new, done, etc."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM jobs")
        total = cur.fetchone()["total"]
        
        cur.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'NEW'")
        new_count = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'DONE'")
        done_count = cur.fetchone()["count"]
        
        return {
            "total": total,
            "new": new_count,
            "done": done_count,
            "active": total - done_count,
        }

    # Modules
    def list_modules(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, description, version, installed FROM modules ORDER BY name"
        )
        return list(cur.fetchall())

    def set_module_installed(self, module_id: str, installed: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE modules SET installed = ? WHERE id = ?",
            (1 if installed else 0, module_id),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


class SidebarFull(ttk.Frame):
    """Full Sidebar with icons + text navigation."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp", ui_engine: UIEngine):
        super().__init__(parent, style="Sidebar.TFrame")
        self.app = app
        self.ui_engine = ui_engine
        self.active_button = None
        self.buttons = {}
        self._build()
    
    def _build(self) -> None:
        """Build sidebar with logo and navigation buttons."""
        colors = self.ui_engine.get_theme()
        
        # Logo area
        logo_frame = ttk.Frame(self, style="Sidebar.TFrame")
        logo_frame.pack(fill="x", pady=(20, 30), padx=12)
        ttk.Label(
            logo_frame,
            text="⚡ Laser Pro",
            style="Sidebar.TLabel",
            font=("Segoe UI", 14, "bold"),
            foreground=colors["sidebar_active"],
        ).pack()
        
        # Navigation buttons - will be updated with translations
        self._build_nav_buttons()
    
    def _build_nav_buttons(self) -> None:
        """Build navigation buttons with current language."""
        lang = self.app.lang_manager
        nav_items = [
            ("🏠", lang.get("dashboard"), "MyStudioFrame"),
            ("📂", lang.get("projects"), "JobsFrame"),
            ("➕", lang.get("new_project"), "NewJobFrame"),
            ("🧿", lang.get("vector_center"), "VectorCenterFrame"),
            ("🔧", lang.get("tools"), "ToolsFrame"),
            ("🧩", lang.get("modules"), "ModulesFrame"),
            ("🌐", lang.get("language"), "LanguageFrame"),
            ("⚙️", lang.get("settings"), "SettingsFrame"),
        ]
        
        # Clear existing buttons
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()
        
        # Rebuild buttons
        for icon, text, frame_name in nav_items:
            btn = ttk.Button(
                self,
                text=f"  {icon}  {text}",
                style="Sidebar.TButton",
                command=lambda fn=frame_name: self._navigate(fn) if fn else None,
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[frame_name or text] = btn
    
    def _navigate(self, frame_name: str) -> None:
        """Navigate to frame and update active state."""
        if frame_name:
            self.app.show_frame(frame_name)
            self._set_active(frame_name)
    
    def _set_active(self, frame_name: str) -> None:
        """Set active button state."""
        colors = self.ui_engine.get_theme()
        # Reset all
        for btn in self.buttons.values():
            btn.state(["!selected"])
        # Set active
        if frame_name in self.buttons:
            btn = self.buttons[frame_name]
            btn.state(["selected"])


class TopMenuBar(ttk.Frame):
    """Top menu bar with Simple and Engineering modes."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp", ui_engine: UIEngine, mode: str = "simple"):
        super().__init__(parent, style="Card.TFrame")
        self.app = app
        self.ui_engine = ui_engine
        self.mode = mode
        self.current_frame = None
        self._build()
    
    def _build(self) -> None:
        """Build top menu based on mode."""
        if self.mode == "simple":
            self._build_simple()
        elif self.mode == "engineering":
            self._build_engineering()
    
    def _build_simple(self) -> None:
        """Simple mode: title + search + language."""
        lang = self.app.lang_manager
        colors = self.ui_engine.get_theme()
        self.configure(style="HeaderBar.TFrame", padding=(10, 6))

        left_frame = ttk.Frame(self, style="HeaderBar.TFrame")
        left_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(left_frame, text="LASER ERP PRO", style="HeaderTitle.TLabel").pack(side="left", padx=(6, 12))
        self.title_label = ttk.Label(left_frame, text=lang.get("dashboard", "Dashboard"), style="HeaderTitle.TLabel")
        self.title_label.pack(side="left", padx=(0, 12))
        ttk.Label(
            left_frame,
            text=f"Business Console • {datetime.now().strftime('%Y-%m-%d')}",
            style="HeaderMeta.TLabel",
        ).pack(side="left")

        right_frame = ttk.Frame(self, style="HeaderBar.TFrame")
        right_frame.pack(side="right", padx=2, pady=0)

        ttk.Button(right_frame, text="🔄", width=3, style="Outline.TButton").pack(side="left", padx=2)
        ttk.Button(
            right_frame,
            text="🌐",
            width=3,
            style="Outline.TButton",
            command=lambda: self.app.show_frame("LanguageFrame"),
        ).pack(side="left", padx=2)
        ttk.Button(
            right_frame,
            text="⚙️",
            width=3,
            style="Outline.TButton",
            command=lambda: self.app.show_frame("SettingsFrame"),
        ).pack(side="left", padx=2)
        # Keep card/outline controls readable over dark header.
        self.ui_engine.style.configure("Outline.TButton", foreground=colors["primary"])
    
    def _build_engineering(self) -> None:
        """Engineering mode: toolbar with context actions."""
        # Left: Page title
        self.title_label = ttk.Label(self, text="Projects", style="Heading.TLabel")
        self.title_label.pack(side="left", padx=16, pady=8)
        
        # Center: Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side="left", padx=20, fill="x", expand=True)
        
        # Context buttons (example for Projects)
        ttk.Button(toolbar, text="New", style="Outline.TButton", width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Duplicate", style="Outline.TButton", width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Export CSV", style="Outline.TButton", width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Filters", style="Outline.TButton", width=10).pack(side="left", padx=2)
        
        # Right: Global actions
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", padx=8, pady=4)
        ttk.Button(right_frame, text="🌐", width=3, style="Outline.TButton").pack(side="left", padx=2)
    
    def update_title(self, title: str) -> None:
        """Update page title."""
        if hasattr(self, "title_label"):
            # Translate title if needed
            lang = self.app.lang_manager
            translated_title = lang.get(title.lower().replace(" ", "_"), title)
            self.title_label.configure(text=translated_title)
    
    def set_mode(self, mode: str) -> None:
        """Switch between simple/engineering mode."""
        self.mode = mode
        for widget in self.winfo_children():
            widget.destroy()
        self._build()


class TopTabsBar(ttk.Frame):
    """Top tabs navigation used in compact industrial layout."""

    def __init__(self, parent: tk.Widget, app: "LaserApp", ui_engine: UIEngine):
        super().__init__(parent, style="TopTabs.TFrame")
        self.app = app
        self.ui_engine = ui_engine
        self.buttons = {}
        self._build()

    def _tabs(self) -> List[Tuple[str, str]]:
        lang = self.app.lang_manager
        return [
            ("MyStudioFrame", f"📊 {lang.get('dashboard')}"),
            ("JobsFrame", f"📂 {lang.get('projects')}"),
            ("NewJobFrame", f"➕ {lang.get('new_project')}"),
            ("VectorCenterFrame", f"🧿 {lang.get('vector_center')}"),
            ("ToolsFrame", f"🔧 {lang.get('tools')}"),
            ("SettingsFrame", f"⚙️ {lang.get('settings')}"),
        ]

    def _build(self) -> None:
        for frame_name, label in self._tabs():
            btn = ttk.Button(
                self,
                text=label,
                style="TabNav.TButton",
                command=lambda n=frame_name: self.app.show_frame(n),
            )
            btn.pack(side="left", padx=2, pady=3)
            self.buttons[frame_name] = btn

    def refresh_labels(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self.buttons = {}
        self._build()

    def set_active(self, frame_name: str) -> None:
        for btn in self.buttons.values():
            btn.state(["!selected"])
        if frame_name in self.buttons:
            self.buttons[frame_name].state(["selected"])


class BaseFrame(ttk.Frame):
    """Common base for all frames to access shared app/database objects."""

    def __init__(self, parent: tk.Widget, app: "LaserApp", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app
        self.db = app.db


class MyStudioFrame(BaseFrame):
    """Professional Dashboard - لوحة التحكم الاحترافية."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.current_job_card = None
        self.today_jobs_card = None
        self.revenue_card = None
        self.notes_card = None
        self._build()
        self.refresh()
    
    def _build(self) -> None:
        """Build dashboard with 4 main cards."""
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=20, pady=(15, 20))
        lang = self.app.lang_manager
        ttk.Label(
            header,
            text=f"⚡ {lang.get('my_studio')}",
            style="Heading.TLabel",
            font=("Segoe UI", 20, "bold"),
        ).pack(side="left")
        ttk.Button(
            header,
            text=f"🔄 {lang.get('refresh')}",
            style="Outline.TButton",
            command=self.refresh,
        ).pack(side="right", padx=5)
        ttk.Label(
            header,
            text=f"📅 {datetime.now().strftime('%Y-%m-%d')}",
            style="Subtle.TLabel",
        ).pack(side="right")
        
        # Cards container (2x2 grid)
        cards_container = ttk.Frame(self)
        cards_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Row 1
        row1 = ttk.Frame(cards_container)
        row1.pack(fill="x", pady=(0, 15))
        
        # Card 1: Current Job
        self.current_job_card = self._create_card(row1, f"🟩 {lang.get('current_job')}", side="left", padx=(0, 15))
        
        # Card 2: Today's Revenue
        self.revenue_card = self._create_card(row1, f"💰 {lang.get('revenue')}", side="left", padx=(0, 15))
        
        # Row 2
        row2 = ttk.Frame(cards_container)
        row2.pack(fill="both", expand=True, pady=(0, 0))
        
        # Card 3: Today's Jobs
        self.today_jobs_card = self._create_card(row2, f"📂 {lang.get('today_jobs')}", side="left", padx=(0, 15), expand=True)
        
        # Card 4: Notes/ToDo
        self.notes_card = self._create_card(row2, f"📝 {lang.get('notes')}", side="left", padx=(0, 0), expand=True)
    
    def _create_card(self, parent: ttk.Frame, title: str, side: str = "left", padx: Tuple[int, int] = (0, 0), expand: bool = False) -> ttk.Frame:
        """Create a card widget with improved spacing."""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(side=side, fill="both", expand=expand, padx=padx)
        card.configure(width=320 if not expand else 420)
        
        # Card title - clearer hierarchy
        title_frame = ttk.Frame(card, style="Card.TFrame")
        title_frame.pack(fill="x", padx=16, pady=(16, 10))
        ttk.Label(title_frame, text=title, style="Heading.TLabel", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        # Content area - more padding
        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        return content
    
    def refresh(self) -> None:
        """Refresh all dashboard data."""
        self._refresh_current_job()
        self._refresh_today_jobs()
        self._refresh_revenue()
        self._refresh_notes()
    
    def _refresh_current_job(self) -> None:
        """Refresh Current Job card."""
        # Clear existing content
        for widget in self.current_job_card.winfo_children():
            widget.destroy()
        
        try:
            job = self.db.get_current_job()
        except Exception as e:
            ttk.Label(
                self.current_job_card,
                text=f"خطأ في تحميل البيانات: {e}",
                style="Subtle.TLabel",
            ).pack(pady=20)
            return
        
        if not job:
            lang = self.app.lang_manager
            ttk.Label(
                self.current_job_card,
                text=lang.get("no_active_job"),
                style="Subtle.TLabel",
            ).pack(pady=20)
            return
        
        # Convert sqlite3.Row to dict for .get() support
        job = dict(job)
        
        # Job details - use get() for safety
        job_name = job.get('name', 'بدون اسم')
        ttk.Label(
            self.current_job_card,
            text=f"📋 {job_name}",
            style="TLabel",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 5))
        
        customer_name = job.get('customer_name')
        if customer_name:
            ttk.Label(
                self.current_job_card,
                text=f"👤 {customer_name}",
                style="TLabel",
            ).pack(anchor="w", pady=2)
        
        material_type = job.get('material_type')
        if material_type:
            plate_size = ""
            plate_width = job.get('plate_width')
            plate_height = job.get('plate_height')
            if plate_width and plate_height:
                plate_size = f" ({plate_width}×{plate_height})"
            ttk.Label(
                self.current_job_card,
                text=f"🔧 {material_type}{plate_size}",
                style="TLabel",
            ).pack(anchor="w", pady=2)
        
        # Status badge
        status_colors = {
            "NEW": "#3B82F6",
            "VECTOR": "#22D3EE",
            "LASER": "#F97316",
            "DONE": "#22C55E",
        }
        job_status = job.get('status', 'NEW')
        status_color = status_colors.get(job_status, "#6B7280")
        status_label = ttk.Label(
            self.current_job_card,
            text=f"● {job_status}",
            style="TLabel",
            foreground=status_color,
            font=("Segoe UI", 10, "bold"),
        )
        status_label.pack(anchor="w", pady=(8, 0))
        
        # Actions
        actions_frame = ttk.Frame(self.current_job_card)
        actions_frame.pack(fill="x", pady=(12, 0))
        
        lang = self.app.lang_manager
        ttk.Button(
            actions_frame,
            text=f"🧿 {lang.get('open_vector')}",
            style="Primary.TButton",
            command=lambda: self.app.show_frame("VectorCenterFrame"),
        ).pack(fill="x", pady=(0, 5))
        
        ttk.Button(
            actions_frame,
            text=f"📂 {lang.get('open_project')}",
            style="Outline.TButton",
            command=lambda: self.app.show_frame("JobsFrame"),
        ).pack(fill="x", pady=(0, 0))
    
    def _refresh_today_jobs(self) -> None:
        """Refresh Today's Jobs card - Table format."""
        for widget in self.today_jobs_card.winfo_children():
            widget.destroy()
        
        jobs = self.db.get_today_jobs()
        
        if not jobs:
            lang = self.app.lang_manager
            ttk.Label(
                self.today_jobs_card,
                text=lang.get("no_today_jobs"),
                style="Subtle.TLabel",
            ).pack(pady=20)
            return
        
        # Table header
        header_frame = ttk.Frame(self.today_jobs_card)
        header_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(header_frame, text="#", style="TLabel", font=("Segoe UI", 9, "bold"), width=4).pack(side="left")
        ttk.Label(header_frame, text="Name", style="TLabel", font=("Segoe UI", 9, "bold"), width=15).pack(side="left", padx=5)
        ttk.Label(header_frame, text="Status", style="TLabel", font=("Segoe UI", 9, "bold"), width=8).pack(side="left", padx=5)
        ttk.Label(header_frame, text="Price", style="TLabel", font=("Segoe UI", 9, "bold"), width=10).pack(side="left", padx=5)
        
        # Jobs rows (convert sqlite3.Row to dict for .get() support)
        for job in jobs[:8]:  # Show max 8
            job = dict(job)
            row_frame = ttk.Frame(self.today_jobs_card)
            row_frame.pack(fill="x", pady=2)
            
            # ID
            job_id = job.get('id', '')
            ttk.Label(row_frame, text=str(job_id), style="TLabel", width=4).pack(side="left")
            
            # Name (truncate if long)
            job_name = job.get('name', 'بدون اسم')
            name = job_name[:20] + "..." if len(job_name) > 20 else job_name
            ttk.Label(row_frame, text=name, style="TLabel", width=15).pack(side="left", padx=5)
            
            # Status with color
            status_colors = {"NEW": "#3B82F6", "VECTOR": "#22D3EE", "LASER": "#F97316", "DONE": "#22C55E"}
            job_status = job.get('status', 'NEW')
            status_color = status_colors.get(job_status, "#6B7280")
            ttk.Label(
                row_frame,
                text=job_status,
                style="TLabel",
                width=8,
                foreground=status_color,
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left", padx=5)
            
            # Price
            job_price = job.get('price')
            price_text = f"{job_price:.0f} DH" if job_price else "-"
            ttk.Label(row_frame, text=price_text, style="TLabel", width=10).pack(side="left", padx=5)
        
        if len(jobs) > 8:
            ttk.Label(
                self.today_jobs_card,
                text=f"... و {len(jobs) - 8} أخرى",
                style="Subtle.TLabel",
            ).pack(pady=(8, 0))
    
    def _refresh_revenue(self) -> None:
        """Refresh Revenue card - Today + Week."""
        for widget in self.revenue_card.winfo_children():
            widget.destroy()
        
        lang = self.app.lang_manager
        today_revenue = self.db.get_today_revenue()
        week_revenue = self.db.get_week_revenue()
        
        # Today Revenue
        ttk.Label(
            self.revenue_card,
            text=f"{lang.get('today')}:",
            style="Subtle.TLabel",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 2))
        
        ttk.Label(
            self.revenue_card,
            text=f"{today_revenue:.0f} DH",
            style="Heading.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground="#22C55E",
        ).pack(anchor="w", pady=(0, 15))
        
        # Week Revenue
        ttk.Label(
            self.revenue_card,
            text=f"{lang.get('week')}:",
            style="Subtle.TLabel",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 2))
        
        ttk.Label(
            self.revenue_card,
            text=f"{week_revenue:.0f} DH",
            style="Heading.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground="#3B82F6",
        ).pack(anchor="w", pady=(0, 10))
        
        # Summary stats
        summary = self.db.get_jobs_summary()
        stats_frame = ttk.Frame(self.revenue_card)
        stats_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(
            stats_frame,
            text=f"📊 Total: {summary['total']}",
            style="TLabel",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=2)
        
        ttk.Label(
            stats_frame,
            text=f"🆕 New: {summary['new']} | ✅ Done: {summary['done']}",
            style="TLabel",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=2)
    
    def _refresh_notes(self) -> None:
        """Refresh Notes/ToDo card - only create widgets once to preserve user content."""
        if self.notes_card.winfo_children():
            return  # Already built - preserve content
        lang = self.app.lang_manager
        notes_text = tk.Text(
            self.notes_card,
            height=8,
            width=30,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=1,
        )
        notes_text.pack(fill="both", expand=True)
        notes_text.insert("1.0", "ملاحظاتك اليومية...\n\n- مشروع جديد\n- مراجعة التصاميم\n- استدعاء الزبون")
        ttk.Button(
            self.notes_card,
            text=f"💾 {lang.get('save_notes')}",
            style="Outline.TButton",
            command=lambda: messagebox.showinfo("", lang.get("notes_saved_later")),
        ).pack(fill="x", pady=(8, 0))


class HomeFrame(BaseFrame):
    """Legacy home frame - kept for compatibility."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        # Redirect to MyStudioFrame
        self._build()
    
    def _build(self) -> None:
        ttk.Label(
            self,
            text="Redirecting to Dashboard...",
            style="Heading.TLabel",
        ).pack(pady=50)


class JobsFrame(BaseFrame):
    """List, search, and delete jobs."""

    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.tree = None
        self.search_entry = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Top bar with search and actions
        top_bar = ttk.Frame(self, style="Card.TFrame")
        top_bar.pack(fill="x", padx=12, pady=(8, 10))
        
        # Search
        search_frame = ttk.Frame(top_bar, style="Card.TFrame")
        search_frame.pack(side="right", padx=5)
        ttk.Label(search_frame, text="بحث:", style="Subtle.TLabel").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side="left", padx=3)
        ttk.Button(search_frame, text="🔍", width=3, style="Outline.TButton", command=self.refresh).pack(side="left")

        ttk.Button(top_bar, text="🔄 تحديث", style="Outline.TButton", command=self.refresh).pack(side="right", padx=5)
        ttk.Button(top_bar, text="🗑 حذف المحدد", style="Primary.TButton", command=self.delete_selected).pack(side="right", padx=5)

        columns = (
            "id",
            "name",
            "customer_name",
            "customer_phone",
            "price",
            "material_type",
            "plate_size",
            "image",
            "created_at",
            "status",
        )
        tree_container = ttk.Frame(self, style="Card.TFrame")
        tree_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15, style="App.Treeview")
        headers = [
            "ID",
            "المشروع",
            "الزبون",
            "الهاتف",
            "الثمن",
            "المادة",
            "المقاس",
            "الصورة",
            "تاريخ الإنشاء",
            "الحالة",
        ]
        for col, text in zip(columns, headers):
            tree.heading(col, text=text)

        tree.column("id", width=40, anchor="center")
        tree.column("name", width=130)
        tree.column("customer_name", width=130)
        tree.column("customer_phone", width=100)
        tree.column("price", width=70, anchor="e")
        tree.column("material_type", width=80)
        tree.column("plate_size", width=90)
        tree.column("image", width=120)
        tree.column("created_at", width=130)
        tree.column("status", width=70, anchor="center")

        tree.pack(fill="both", expand=True, padx=6, pady=6)

        even_bg, odd_bg = self.app.ui_engine.get_tree_row_colors()
        tree.tag_configure("even", background=even_bg)
        tree.tag_configure("odd", background=odd_bg)

        self.tree = tree

    def refresh(self) -> None:
        search_text = self.search_entry.get().strip() if self.search_entry else None

        # Update tree colors from current theme
        even_bg, odd_bg = self.app.ui_engine.get_tree_row_colors()
        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)

        for row in self.tree.get_children():
            self.tree.delete(row)

        jobs = self.db.list_jobs(search_text=search_text if search_text else None)
        for idx, job in enumerate(jobs):
            j = dict(job)  # sqlite3.Row -> dict for compatibility
            job_id = j.get("id")
            name = j.get("name", "")
            customer_name = j.get("customer_name", "")
            customer_phone = j.get("customer_phone", "")
            price = j.get("price")
            material_type = j.get("material_type", "")
            plate_width = j.get("plate_width")
            plate_height = j.get("plate_height")
            image_path = j.get("image_path", "")
            created_at = j.get("created_at", "")
            status = j.get("status", "")
            short_image = os.path.basename(image_path) if image_path else ""
            plate_size = ""
            if plate_width and plate_height:
                plate_size = f"{plate_width}×{plate_height}"
            price_str = f"{price:.2f}" if price is not None else ""
            tag = "odd" if idx % 2 else "even"
            self.tree.insert(
                "",
                "end",
                tags=(tag,),
                values=(
                    job_id,
                    name,
                    customer_name or "",
                    customer_phone or "",
                    price_str,
                    material_type or "",
                    plate_size,
                    short_image,
                    created_at,
                    status,
                ),
            )

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        lang = self.app.lang_manager
        if not selected:
            messagebox.showinfo("", lang.get("select_job"))
            return
        if not messagebox.askyesno("", lang.get("confirm_delete")):
            return
        for item in selected:
            job_id = self.tree.item(item, "values")[0]
            self.db.delete_job(int(job_id))
        self.refresh()


class NewJobFrame(BaseFrame):
    """Form to create a new job entry."""

    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.entry_name = None
        self.entry_image = None
        self.entry_customer_name = None
        self.entry_customer_phone = None
        self.entry_price = None
        self.text_notes = None
        self.entry_width = None
        self.entry_height = None
        self.combo_material = None
        self._build()

    def _build(self) -> None:
        form = ttk.Frame(self, style="Card.TFrame")
        form.pack(pady=10, padx=16, fill="x")

        row = 0
        # project name
        ttk.Label(form, text="اسم المشروع:").grid(row=row, column=0, sticky="w", pady=3)
        self.entry_name = ttk.Entry(form, width=40)
        self.entry_name.grid(row=row, column=1, sticky="w", pady=3)
        row += 1

        # customer info
        ttk.Label(form, text="اسم الزبون:").grid(row=row, column=0, sticky="w", pady=3)
        self.entry_customer_name = ttk.Entry(form, width=40)
        self.entry_customer_name.grid(row=row, column=1, sticky="w", pady=3)
        row += 1

        ttk.Label(form, text="هاتف الزبون:").grid(row=row, column=0, sticky="w", pady=3)
        self.entry_customer_phone = ttk.Entry(form, width=40)
        self.entry_customer_phone.grid(row=row, column=1, sticky="w", pady=3)
        row += 1

        # price
        ttk.Label(form, text="الثمن (اختياري):").grid(row=row, column=0, sticky="w", pady=3)
        self.entry_price = ttk.Entry(form, width=20)
        self.entry_price.grid(row=row, column=1, sticky="w", pady=3)
        row += 1

        # plate size
        ttk.Label(form, text="مقاس اللوح (عرض × طول، مثلاً بالسم):").grid(row=row, column=0, sticky="w", pady=3)
        size_frame = ttk.Frame(form)
        size_frame.grid(row=row, column=1, sticky="w", pady=3)
        self.entry_width = ttk.Entry(size_frame, width=10)
        ttk.Label(size_frame, text="عرض:").pack(side="left")
        self.entry_width.pack(side="left", padx=3)
        self.entry_height = ttk.Entry(size_frame, width=10)
        ttk.Label(size_frame, text="طول:").pack(side="left")
        self.entry_height.pack(side="left", padx=3)
        row += 1

        # material type
        ttk.Label(form, text="نوع المادة:").grid(row=row, column=0, sticky="w", pady=3)
        self.combo_material = ttk.Combobox(
            form,
            values=["حديد", "ستيل", "ألمنيوم", "نحاس", "خشب", "أكريليك", "أخرى"],
            state="readonly",
            width=20,
        )
        self.combo_material.grid(row=row, column=1, sticky="w", pady=3)
        self.combo_material.set("حديد")
        row += 1

        # image
        ttk.Label(form, text="الصورة (اختيار من الجهاز):").grid(row=row, column=0, sticky="w", pady=3)
        img_frame = ttk.Frame(form)
        img_frame.grid(row=row, column=1, sticky="w", pady=3)

        self.entry_image = ttk.Entry(img_frame, width=40)
        self.entry_image.pack(side="left")

        ttk.Button(img_frame, text="استعراض...", command=self.browse_image).pack(side="left", padx=5)
        row += 1

        # notes
        ttk.Label(form, text="ملاحظات (اختياري):").grid(row=row, column=0, sticky="nw", pady=3)
        self.text_notes = tk.Text(form, width=40, height=4)
        self.text_notes.grid(row=row, column=1, sticky="w", pady=3)
        row += 1

        ttk.Button(self, text="💾 حفظ المشروع", style="Primary.TButton", command=self.save_job).pack(
            pady=12, padx=16, fill="x"
        )

        note = ttk.Label(
            self,
            text=(
                "ملاحظة: دابا كنخزنو كل معلومات المشروع (اسم، زبون، ثمن، مادة، مقاس، صورة، ملاحظات).\n"
                "في المراحل القادمة يمكن نزيدو معالجة بالـAI وتوليد DXF/SVG وربط مباشر مع ماكينة اللايزر."
            ),
            justify="center",
            style="Subtle.TLabel",
        )
        note.pack(pady=5)

    def browse_image(self) -> None:
        filename = filedialog.askopenfilename(
            title="اختيار صورة",
            filetypes=(
                ("صور", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All files", "*.*"),
            ),
        )
        if filename:
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, filename)

    def save_job(self) -> None:
        name = self.entry_name.get().strip()
        customer_name = self.entry_customer_name.get().strip()
        customer_phone = self.entry_customer_phone.get().strip()
        price_text = self.entry_price.get().strip()
        image_path = self.entry_image.get().strip()
        notes = self.text_notes.get("1.0", tk.END).strip()
        width_text = self.entry_width.get().strip()
        height_text = self.entry_height.get().strip()
        material_type = self.combo_material.get().strip() if self.combo_material else ""

        if not name:
            messagebox.showerror("خطأ", "اسم المشروع ضروري.")
            return

        price = None
        if price_text:
            try:
                price = float(price_text)
            except ValueError:
                messagebox.showerror("خطأ", "الثمن يجب أن يكون رقماً (مثلاً 150 أو 150.5).")
                return

        plate_width = None
        plate_height = None
        if width_text:
            try:
                plate_width = float(width_text)
            except ValueError:
                messagebox.showerror("خطأ", "العرض يجب أن يكون رقماً.")
                return
        if height_text:
            try:
                plate_height = float(height_text)
            except ValueError:
                messagebox.showerror("خطأ", "الطول يجب أن يكون رقماً.")
                return

        try:
            self.db.create_job(
                name=name,
                image_path=image_path,
                customer_name=customer_name,
                customer_phone=customer_phone,
                price=price,
                notes=notes,
                plate_width=plate_width,
                plate_height=plate_height,
                material_type=material_type,
            )
            messagebox.showinfo("نجاح", "تم حفظ المشروع بنجاح.")
            self._clear_form()
        except Exception as e:
            messagebox.showerror("خطأ", f"وقع خطأ أثناء الحفظ:\n{e}")

    def _clear_form(self) -> None:
        self.entry_name.delete(0, tk.END)
        self.entry_customer_name.delete(0, tk.END)
        self.entry_customer_phone.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_image.delete(0, tk.END)
        self.entry_width.delete(0, tk.END)
        self.entry_height.delete(0, tk.END)
        self.combo_material.set("حديد")
        self.text_notes.delete("1.0", tk.END)
class ModulesFrame(BaseFrame):
    """Display and toggle optional modules."""

    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.tree = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        # Top bar with actions
        top_bar = ttk.Frame(self, style="Card.TFrame")
        top_bar.pack(fill="x", padx=12, pady=(8, 10))
        
        ttk.Button(top_bar, text="🔄 تحديث", style="Outline.TButton", command=self.refresh).pack(side="right", padx=5)
        ttk.Button(top_bar, text="تفعيل / تعطيل", style="Primary.TButton", command=self.toggle_selected).pack(side="right", padx=5)

        columns = ("id", "name", "description", "version", "installed")
        tree_container = ttk.Frame(self, style="Card.TFrame")
        tree_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15, style="App.Treeview")
        for col, text in zip(columns, ["ID", "الاسم", "الوصف", "النسخة", "مثبّت؟"]):
            tree.heading(col, text=text)

        tree.column("id", width=120)
        tree.column("name", width=150)
        tree.column("description", width=250)
        tree.column("version", width=80, anchor="center")
        tree.column("installed", width=80, anchor="center")

        tree.pack(fill="both", expand=True, padx=6, pady=6)
        even_bg, odd_bg = self.app.ui_engine.get_tree_row_colors()
        tree.tag_configure("even", background=even_bg)
        tree.tag_configure("odd", background=odd_bg)
        self.tree = tree

    def refresh(self) -> None:
        # Update tree colors from current theme
        even_bg, odd_bg = self.app.ui_engine.get_tree_row_colors()
        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)

        for row in self.tree.get_children():
            self.tree.delete(row)

        modules = self.db.list_modules()
        lang = self.app.lang_manager
        yes_no = (lang.get("yes"), lang.get("no"))
        for idx, m in enumerate(modules):
            row = dict(m)
            module_id = row.get("id", "")
            name = row.get("name", "")
            desc = row.get("description", "")
            ver = row.get("version", "")
            installed = row.get("installed", 0)
            self.tree.insert(
                "",
                "end",
                tags=("odd" if idx % 2 else "even",),
                values=(module_id, name, desc, ver, yes_no[0] if installed else yes_no[1]),
            )

    def toggle_selected(self) -> None:
        selected = self.tree.selection()
        lang = self.app.lang_manager
        if not selected:
            messagebox.showinfo("", lang.get("select_module"))
            return
        lang = self.app.lang_manager
        yes_label = lang.get("yes")
        for item in selected:
            values = self.tree.item(item, "values")
            module_id = values[0]
            installed_str = values[4]
            new_installed = installed_str != yes_label
            self.db.set_module_installed(module_id, new_installed)
        self.refresh()


class VectorCenterFrame(BaseFrame):
    """
    مركز الفكتور:
    - أدوات تحضير الصورة قبل الفكتور (أبيض/أسود، إزالة الخلفية تقريبياً...)
    - مستقبلاً: ربط بالـAI و توليد SVG/DXF و G-code.
    """

    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.entry_input = None
        self.entry_output = None
        self.workflow_status = None
        self.selected_job_id = None
        self.jobs_combo = None
        self._jobs_index = []
        self._build()

    def _build(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # اختيار مشروع (Job)
        job_frame = ttk.LabelFrame(body, text="اختيار مشروع (اختياري)")
        job_frame.pack(fill="x", pady=5)

        self.jobs_combo = ttk.Combobox(job_frame, state="readonly", width=50)
        self.jobs_combo.pack(side="left", padx=5, pady=5)
        ttk.Button(job_frame, text="تحميل الصورة من المشروع", command=self.load_from_job).pack(
            side="left", padx=5
        )

        # إدخال وإخراج
        paths_frame = ttk.LabelFrame(body, text="ملفات الإدخال و الإخراج")
        paths_frame.pack(fill="x", pady=5)

        ttk.Label(paths_frame, text="صورة الإدخال:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_input = ttk.Entry(paths_frame, width=60)
        self.entry_input.grid(row=0, column=1, sticky="w", pady=3)
        ttk.Button(
            paths_frame, text="اختيار...", command=self.browse_input
        ).grid(row=0, column=2, padx=5)

        ttk.Label(paths_frame, text="ملف الإخراج:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_output = ttk.Entry(paths_frame, width=60)
        self.entry_output.grid(row=1, column=1, sticky="w", pady=3)
        ttk.Button(
            paths_frame, text="اختيار مجلد...", command=self.choose_output_folder
        ).grid(row=1, column=2, padx=5)

        # أدوات الفكتور - شبكة من عمودين
        tools_frame = ttk.LabelFrame(body, text="🛠️ أدوات التحضير (Raster Prep Tools)")
        tools_frame.pack(fill="x", pady=10)

        tools_list = [
            ("تحويل أبيض/أسود (Threshold)", self.to_black_and_white),
            ("تنظيف الخلفية (أبيض→شفاف)", self.remove_background),
            ("تخفيض الضجيج (Blur)", self.light_blur),
            ("عكس الألوان (Invert)", self.invert_image),
            ("تعديل التباين (Contrast)", self.adjust_contrast),
            ("تغيير الحجم (Resize)", self.resize_image),
            ("رمادي (Grayscale)", self.to_grayscale),
            ("تعديل السطوع (Brightness)", self.adjust_brightness),
            ("زيادة الحدّة (Sharpen)", self.sharpen_image),
            ("تحسين تلقائي (Auto Contrast)", self.auto_contrast),
            ("إبراز الحواف (Edge Detect)", self.edge_detect),
            ("قص الهوامش البيضاء (Trim Margins)", self.trim_white_margins),
            ("تدوير 90°", lambda: self.rotate_image(90)),
            ("تدوير 180°", lambda: self.rotate_image(180)),
            ("تدوير 270°", lambda: self.rotate_image(270)),
            ("عكس أفقي (Mirror H)", lambda: self.flip_image("h")),
            ("عكس عمودي (Mirror V)", lambda: self.flip_image("v")),
            ("Dither للايزر", self.dither_image),
        ]
        for i, (label, cmd) in enumerate(tools_list):
            r, c = divmod(i, 2)
            ttk.Button(
                tools_frame,
                text=label,
                command=cmd,
                width=28,
                style="Outline.TButton",
            ).grid(row=r, column=c, pady=3, padx=5, sticky="w")

        workflow_frame = ttk.LabelFrame(body, text="⚙️ Workflow جاهز / Production Presets")
        workflow_frame.pack(fill="x", pady=8)

        wf_row1 = ttk.Frame(workflow_frame)
        wf_row1.pack(fill="x", padx=5, pady=4)
        ttk.Button(
            wf_row1,
            text="Preset: Logo/Texts (Sharp B&W)",
            command=lambda: self.run_preset("logo"),
            style="Primary.TButton",
        ).pack(side="left", padx=4)
        ttk.Button(
            wf_row1,
            text="Preset: Photo Engraving",
            command=lambda: self.run_preset("photo"),
            style="Outline.TButton",
        ).pack(side="left", padx=4)

        wf_row2 = ttk.Frame(workflow_frame)
        wf_row2.pack(fill="x", padx=5, pady=(0, 4))
        ttk.Button(
            wf_row2,
            text="Batch Folder: Logo Preset",
            command=lambda: self.run_batch_preset("logo"),
            style="Outline.TButton",
        ).pack(side="left", padx=4)
        ttk.Button(
            wf_row2,
            text="Batch Folder: Photo Preset",
            command=lambda: self.run_batch_preset("photo"),
            style="Outline.TButton",
        ).pack(side="left", padx=4)

        self.workflow_status = ttk.Label(
            workflow_frame,
            text="Workflow: اختَر preset وطبّقه مباشرة على ملف واحد أو مجلد كامل.",
            style="Subtle.TLabel",
        )
        self.workflow_status.pack(anchor="w", padx=8, pady=(2, 6))

        note = ttk.Label(
            body,
            text=(
                "هذه الأدوات تقوم فقط بتحضير الصورة قبل الفكتور.\n"
                "الآن تمت إضافة workflows جاهزة، والمرحلة القادمة: توليد SVG/DXF و G-code."
            ),
            justify="center",
            style="Subtle.TLabel",
        )
        note.pack(pady=10)
    def refresh(self) -> None:
        # تعبئة قائمة المشاريع
        jobs = self.db.list_jobs()
        labels = []
        self._jobs_index = []
        for j in jobs:
            row = dict(j)
            job_id = row.get("id")
            name = row.get("name", "")
            customer_name = row.get("customer_name", "")
            image_path = row.get("image_path", "")
            label = f"[{job_id}] {name}"
            if customer_name:
                label += f" - {customer_name}"
            labels.append(label)
            self._jobs_index.append((job_id, image_path))
        if labels:
            self.jobs_combo["values"] = labels
        else:
            self.jobs_combo["values"] = []
        self.jobs_combo.set("")

    def browse_input(self) -> None:
        fn = filedialog.askopenfilename(
            title="اختيار صورة الإدخال",
            filetypes=(
                ("صور", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All files", "*.*"),
            ),
        )
        if fn:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, fn)

    def choose_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="اختيار مجلد الإخراج")
        if not folder:
            return
        in_path = self.entry_input.get().strip()
        base_name = "output"
        if in_path:
            base_name = os.path.splitext(os.path.basename(in_path))[0] + "_proc"
        out_path = os.path.join(folder, base_name + ".png")
        self.entry_output.delete(0, tk.END)
        self.entry_output.insert(0, out_path)

    def load_from_job(self) -> None:
        if not self.jobs_combo.get():
            messagebox.showinfo("معلومة", "اختر مشروعاً من اللائحة أولاً.")
            return
        idx = self.jobs_combo.current()
        if idx < 0:
            return
        job_id, image_path = self._jobs_index[idx]
        self.selected_job_id = job_id
        if image_path:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, image_path)
        else:
            messagebox.showinfo("معلومة", "هذا المشروع لا يتوفر على صورة مسجلة.")

    def _ensure_pillow(self) -> bool:
        if not PIL_AVAILABLE:
            messagebox.showerror(
                "مكتبة ناقصة",
                "مكتبة Pillow غير مثبتة.\nمن فضلك ثبّت المكتبة بالأمر:\n\npip install pillow",
            )
            return False
        return True

    def _get_paths(self) -> Tuple[Optional[str], Optional[str]]:
        in_path = self.entry_input.get().strip()
        out_path = self.entry_output.get().strip()
        if not in_path:
            messagebox.showerror("خطأ", "مسار صورة الإدخال فارغ.")
            return None, None
        if not os.path.isfile(in_path):
            messagebox.showerror("خطأ", "صورة الإدخال غير موجودة.")
            return None, None
        if not out_path:
            # إذا لم يحدد المستخدم ملف إخراج، نضعه ف نفس المجلد
            base_name = os.path.splitext(os.path.basename(in_path))[0] + "_proc.png"
            out_path = os.path.join(os.path.dirname(in_path), base_name)
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, out_path)
        return in_path, out_path

    def to_black_and_white(self) -> None:
        """B&W with configurable threshold."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        thresh = self._ask_threshold(128)
        if thresh is None:
            return
        try:
            img = Image.open(in_path).convert("L")
            bw = img.point(lambda x: 255 if x > thresh else 0, "1")
            bw = bw.convert("L")
            bw.save(out_path)
            messagebox.showinfo("نجاح", f"تم تحويل الصورة (threshold={thresh}):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def remove_background(self) -> None:
        """Remove white background - configurable sensitivity (threshold 0-255)."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        thresh = self._ask_threshold(240)  # 240 = near white
        if thresh is None:
            return
        try:
            img = Image.open(in_path).convert("RGBA")
            datas = img.getdata()
            new_data = []
            for item in datas:
                r, g, b, a = item
                if r > thresh and g > thresh and b > thresh:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append((r, g, b, a))
            img.putdata(new_data)
            img.save(out_path)
            messagebox.showinfo("نجاح", f"تمت إزالة الخلفية (threshold={thresh}):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def light_blur(self) -> None:
        if not self._ensure_pillow():
            return
        from PIL import ImageFilter  # import here to avoid error if Pillow missing

        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path)
            blurred = img.filter(ImageFilter.MedianFilter(size=3))
            blurred.save(out_path)
            messagebox.showinfo("نجاح", f"تم تخفيض الضجيج (Blur خفيف):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"وقع خطأ أثناء المعالجة:\n{e}")

    def invert_image(self) -> None:
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path).convert("RGB")
            from PIL import ImageOps
            inverted = ImageOps.invert(img)
            inverted.save(out_path)
            messagebox.showinfo("نجاح", f"تم عكس الألوان:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"وقع خطأ أثناء المعالجة:\n{e}")

    def adjust_contrast(self) -> None:
        """Contrast with configurable factor."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        factor = self._ask_float("معامل التباين (1.0=عادي، 1.5=أقوى)", 1.5, 0.5, 3.0)
        if factor is None:
            return
        try:
            from PIL import ImageEnhance
            img = Image.open(in_path).convert("RGB")
            enhancer = ImageEnhance.Contrast(img)
            enhanced = enhancer.enhance(factor)
            enhanced.save(out_path)
            messagebox.showinfo("نجاح", f"تم تعديل التباين ({factor}x):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def resize_image(self) -> None:
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img_preview = Image.open(in_path)
            w_cur, h_cur = img_preview.size
        except Exception:
            w_cur, h_cur = 0, 0
        dialog = tk.Toplevel(self)
        dialog.title("تغيير الحجم")
        dialog.geometry("320x140")
        ttk.Label(dialog, text=f"الحجم الحالي: {w_cur} × {h_cur} px").pack(pady=5)
        ttk.Label(dialog, text="العرض الجديد (px) - يحافظ على النسبة:").pack(pady=2)
        entry_width = ttk.Entry(dialog, width=15)
        entry_width.insert(0, str(w_cur) if w_cur else "")
        entry_width.pack(pady=2)
        def do_resize():
            try:
                w_str = entry_width.get().strip()
                if not w_str:
                    messagebox.showwarning("تنبيه", "أدخل العرض الجديد (بالبكسل)")
                    return
                img = Image.open(in_path)
                new_w = int(w_str)
                if new_w <= 0:
                    raise ValueError("العرض يجب أن يكون أكبر من 0")
                ratio = new_w / img.width
                new_h = int(img.height * ratio)
                resized = img.resize((new_w, new_h), Image.LANCZOS)
                resized.save(out_path)
                dialog.destroy()
                messagebox.showinfo("نجاح", f"تم تغيير الحجم:\n{out_path}")
            except (ValueError, Exception) as e:
                messagebox.showerror("خطأ", str(e))
        ttk.Button(dialog, text="تطبيق", command=do_resize, style="Primary.TButton").pack(pady=10)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

    def to_grayscale(self) -> None:
        """Convert to grayscale (keeps shades)."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path).convert("L")
            img.save(out_path)
            messagebox.showinfo("نجاح", f"تم التحويل إلى رمادي:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def adjust_brightness(self) -> None:
        """Adjust brightness with configurable factor."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        factor = self._ask_float("معامل السطوع (1.0=عادي، 1.5=أفتح)", 1.2, 0.3, 3.0)
        if factor is None:
            return
        try:
            from PIL import ImageEnhance
            img = Image.open(in_path).convert("RGB")
            enhancer = ImageEnhance.Brightness(img)
            enhanced = enhancer.enhance(factor)
            enhanced.save(out_path)
            messagebox.showinfo("نجاح", f"تم تعديل السطوع ({factor}x):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def sharpen_image(self) -> None:
        """Sharpen image."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            from PIL import ImageFilter
            img = Image.open(in_path).convert("RGB")
            sharpened = img.filter(ImageFilter.SHARPEN)
            sharpened.save(out_path)
            messagebox.showinfo("نجاح", f"تم زيادة الحدّة:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def rotate_image(self, angle: int) -> None:
        """Rotate image by angle (90, 180, 270)."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path)
            rotated = img.rotate(-angle, expand=True)
            rotated.save(out_path)
            messagebox.showinfo("نجاح", f"تم التدوير {angle}°:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def flip_image(self, direction: str) -> None:
        """Flip image horizontally (h) or vertically (v)."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            from PIL import ImageOps
            img = Image.open(in_path)
            flipped = ImageOps.mirror(img) if direction == "h" else ImageOps.flip(img)
            flipped.save(out_path)
            messagebox.showinfo("نجاح", f"تم العكس:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def dither_image(self) -> None:
        """Floyd-Steinberg dithering - useful for laser engraving (grayscale to B&W)."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path).convert("L")
            dither = getattr(Image, "Dither", None)
            if dither:
                img = img.convert("1", dither=dither.FLOYDSTEINBERG)
            else:
                img = img.convert("1")  # default uses dithering
            img = img.convert("L")
            img.save(out_path)
            messagebox.showinfo("نجاح", f"تم Dither:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def auto_contrast(self) -> None:
        """Auto contrast enhancement with small clipping."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            from PIL import ImageOps
            img = Image.open(in_path).convert("L")
            result = ImageOps.autocontrast(img, cutoff=1)
            result.save(out_path)
            messagebox.showinfo("نجاح", f"تم التحسين التلقائي:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def edge_detect(self) -> None:
        """Highlight edges to help vector tracing."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            from PIL import ImageFilter
            img = Image.open(in_path).convert("L")
            edges = img.filter(ImageFilter.FIND_EDGES)
            edges.save(out_path)
            messagebox.showinfo("نجاح", f"تم استخراج الحواف:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def trim_white_margins(self) -> None:
        """Trim near-white margins around drawing."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            from PIL import ImageOps
            img = Image.open(in_path).convert("RGB")
            gray = img.convert("L")
            # Invert so content becomes bright, then detect bounding box.
            inv = ImageOps.invert(gray)
            bbox = inv.getbbox()
            if not bbox:
                messagebox.showinfo("معلومة", "لم يتم العثور على محتوى قابل للقص.")
                return
            cropped = img.crop(bbox)
            cropped.save(out_path)
            messagebox.showinfo("نجاح", f"تم قص الهوامش:\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def _apply_logo_preset(self, img: "Image.Image") -> "Image.Image":
        """Pipeline for logos/text: contrast + threshold for clean edges."""
        from PIL import ImageEnhance, ImageOps
        gray = img.convert("L")
        gray = ImageOps.autocontrast(gray, cutoff=1)
        gray = ImageEnhance.Contrast(gray).enhance(1.7)
        bw = gray.point(lambda x: 255 if x > 145 else 0, "1").convert("L")
        return bw

    def _apply_photo_preset(self, img: "Image.Image") -> "Image.Image":
        """Pipeline for photos: smoother grayscale + dither for engraving."""
        from PIL import ImageEnhance, ImageFilter, ImageOps
        gray = img.convert("L")
        gray = ImageOps.autocontrast(gray, cutoff=1)
        gray = ImageEnhance.Contrast(gray).enhance(1.25)
        gray = gray.filter(ImageFilter.MedianFilter(size=3))
        dither = getattr(Image, "Dither", None)
        if dither:
            return gray.convert("1", dither=dither.FLOYDSTEINBERG).convert("L")
        return gray.convert("1").convert("L")

    def run_preset(self, preset_name: str) -> None:
        """Run selected preset for current single file."""
        if not self._ensure_pillow():
            return
        in_path, out_path = self._get_paths()
        if not in_path:
            return
        try:
            img = Image.open(in_path)
            if preset_name == "logo":
                processed = self._apply_logo_preset(img)
                preset_title = "Logo"
            else:
                processed = self._apply_photo_preset(img)
                preset_title = "Photo"
            processed.save(out_path)
            if self.workflow_status is not None:
                self.workflow_status.config(text=f"Workflow: preset {preset_title} تم بنجاح.")
            messagebox.showinfo("نجاح", f"تم تطبيق preset ({preset_title}):\n{out_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def run_batch_preset(self, preset_name: str) -> None:
        """Apply preset to all images in a folder."""
        if not self._ensure_pillow():
            return
        in_dir = filedialog.askdirectory(title="اختيار مجلد الصور (Input Folder)")
        if not in_dir:
            return
        out_dir = filedialog.askdirectory(title="اختيار مجلد الإخراج (Output Folder)")
        if not out_dir:
            return

        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        files = [f for f in os.listdir(in_dir) if os.path.splitext(f.lower())[1] in exts]
        if not files:
            messagebox.showinfo("معلومة", "لم يتم العثور على صور في المجلد.")
            return

        ok_count = 0
        fail_count = 0
        suffix = "logo" if preset_name == "logo" else "photo"

        for fname in files:
            src = os.path.join(in_dir, fname)
            base = os.path.splitext(fname)[0]
            dst = os.path.join(out_dir, f"{base}_{suffix}.png")
            try:
                img = Image.open(src)
                if preset_name == "logo":
                    out_img = self._apply_logo_preset(img)
                else:
                    out_img = self._apply_photo_preset(img)
                out_img.save(dst)
                ok_count += 1
            except Exception:
                fail_count += 1

        if self.workflow_status is not None:
            self.workflow_status.config(text=f"Workflow Batch: نجاح {ok_count} | فشل {fail_count}")
        messagebox.showinfo(
            "Batch Completed",
            f"تمت المعالجة.\nنجاح: {ok_count}\nفشل: {fail_count}\nالإخراج: {out_dir}",
        )

    def _ask_threshold(self, default: int = 128) -> Optional[int]:
        """Dialog to get threshold value (0-255)."""
        dialog = tk.Toplevel(self)
        dialog.title("قيمة Threshold")
        dialog.geometry("280x100")
        result = [None]
        ttk.Label(dialog, text="قيمة الحد (0-255، 128 افتراضي):").pack(pady=5)
        entry = ttk.Entry(dialog, width=10)
        entry.insert(0, str(default))
        entry.pack(pady=2)
        def ok():
            try:
                v = int(entry.get().strip())
                if 0 <= v <= 255:
                    result[0] = v
                    dialog.destroy()
                else:
                    messagebox.showwarning("", "أدخل قيمة بين 0 و 255")
            except ValueError:
                messagebox.showwarning("", "أدخل رقماً صحيحاً")
        ttk.Button(dialog, text="تطبيق", command=ok, style="Primary.TButton").pack(pady=10)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.wait_window()
        return result[0]

    def _ask_float(self, label: str, default: float, min_val: float, max_val: float) -> Optional[float]:
        """Dialog to get float value."""
        dialog = tk.Toplevel(self)
        dialog.title("إدخال القيمة")
        dialog.geometry("320x100")
        result = [None]
        ttk.Label(dialog, text=f"{label} ({min_val}-{max_val}):").pack(pady=5)
        entry = ttk.Entry(dialog, width=10)
        entry.insert(0, str(default))
        entry.pack(pady=2)
        def ok():
            try:
                v = float(entry.get().strip().replace(",", "."))
                if min_val <= v <= max_val:
                    result[0] = v
                    dialog.destroy()
                else:
                    messagebox.showwarning("", f"أدخل قيمة بين {min_val} و {max_val}")
            except ValueError:
                messagebox.showwarning("", "أدخل رقماً صحيحاً")
        ttk.Button(dialog, text="تطبيق", command=ok, style="Primary.TButton").pack(pady=10)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.wait_window()
        return result[0]


class ToolsFrame(BaseFrame):
    """
    أدوات مساعدة للورشة / Workshop utility tools:
    - Unit converter (mm ↔ cm ↔ inches)
    - Engraving time calculator
    - Quick reference
    """

    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self._build()

    def _build(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        intro = ttk.LabelFrame(body, text="🚀 أدوات الورشة الذكية / Smart Workshop Tools")
        intro.pack(fill="x", pady=(0, 10))
        ttk.Label(
            intro,
            text=(
                "هذه الصفحة مطوّرة لتسريع الشغل اليومي: التحويلات، تقدير الوقت، التسعير، "
                "وتجهيز الملفات بسرعة."
            ),
            style="Subtle.TLabel",
            justify="left",
        ).pack(anchor="w", padx=10, pady=8)

        # --- Unit Converter ---
        conv_frame = ttk.LabelFrame(body, text="🔄 محول الوحدات / Unit Converter (mm ↔ cm ↔ inches)")
        conv_frame.pack(fill="x", pady=(0, 10))

        row1 = ttk.Frame(conv_frame)
        row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="mm:", width=8).pack(side="left", padx=5)
        self.entry_mm = ttk.Entry(row1, width=15)
        self.entry_mm.pack(side="left", padx=5)
        ttk.Button(row1, text="→ تحويل", command=self._convert_from_mm, style="Outline.TButton").pack(side="left", padx=5)

        row2 = ttk.Frame(conv_frame)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="cm:", width=8).pack(side="left", padx=5)
        self.entry_cm = ttk.Entry(row2, width=15)
        self.entry_cm.pack(side="left", padx=5)
        ttk.Button(row2, text="→ تحويل", command=self._convert_from_cm, style="Outline.TButton").pack(side="left", padx=5)

        row3 = ttk.Frame(conv_frame)
        row3.pack(fill="x", pady=5)
        ttk.Label(row3, text="inches:", width=8).pack(side="left", padx=5)
        self.entry_inches = ttk.Entry(row3, width=15)
        self.entry_inches.pack(side="left", padx=5)
        ttk.Button(row3, text="→ تحويل", command=self._convert_from_inches, style="Outline.TButton").pack(side="left", padx=5)

        # --- Engraving Time Calculator ---
        calc_frame = ttk.LabelFrame(body, text="⏱️ حساب وقت النقش / Engraving Time Calculator")
        calc_frame.pack(fill="x", pady=(0, 10))

        calc_row1 = ttk.Frame(calc_frame)
        calc_row1.pack(fill="x", pady=5)
        ttk.Label(calc_row1, text="المسافة (mm):", width=14).pack(side="left", padx=5)
        self.entry_distance = ttk.Entry(calc_row1, width=12)
        self.entry_distance.pack(side="left", padx=5)
        ttk.Label(calc_row1, text="السرعة (mm/min):", width=14).pack(side="left", padx=5)
        self.entry_speed = ttk.Entry(calc_row1, width=12)
        self.entry_speed.pack(side="left", padx=5)
        ttk.Button(calc_row1, text="حساب", command=self._calc_engraving_time, style="Primary.TButton").pack(side="left", padx=5)

        self.label_time_result = ttk.Label(calc_frame, text="", style="TLabel", font=("Segoe UI", 10, "bold"))
        self.label_time_result.pack(anchor="w", padx=10, pady=(0, 5))

        # --- Quick Actions ---
        actions_frame = ttk.LabelFrame(body, text="🔗 روابط سريعة / Quick Links")
        actions_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            actions_frame,
            text="🧿 فتح مركز الفكتور (تحضير الصور)",
            command=lambda: self.app.show_frame("VectorCenterFrame"),
            style="Outline.TButton",
        ).pack(fill="x", pady=3, padx=5)

        ttk.Button(
            actions_frame,
            text="📂 فتح المشاريع",
            command=lambda: self.app.show_frame("JobsFrame"),
            style="Outline.TButton",
        ).pack(fill="x", pady=3, padx=5)

        ttk.Button(
            actions_frame,
            text="➕ مشروع جديد",
            command=lambda: self.app.show_frame("NewJobFrame"),
            style="Outline.TButton",
        ).pack(fill="x", pady=3, padx=5)

        # --- Backup DB ---
        backup_frame = ttk.LabelFrame(body, text="💾 نسخ احتياطي / Backup")
        backup_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            backup_frame,
            text="نسخ قاعدة البيانات إلى ملف...",
            command=self._backup_db,
            style="Outline.TButton",
        ).pack(fill="x", pady=5, padx=5)

        # --- Quote Estimator ---
        quote_frame = ttk.LabelFrame(body, text="💰 تقدير السعر / Smart Quote Estimator")
        quote_frame.pack(fill="x", pady=(0, 10))

        q_row1 = ttk.Frame(quote_frame)
        q_row1.pack(fill="x", pady=4)
        ttk.Label(q_row1, text="العرض (mm):", width=14).pack(side="left", padx=5)
        self.entry_q_width = ttk.Entry(q_row1, width=10)
        self.entry_q_width.pack(side="left", padx=5)
        ttk.Label(q_row1, text="الارتفاع (mm):", width=14).pack(side="left", padx=5)
        self.entry_q_height = ttk.Entry(q_row1, width=10)
        self.entry_q_height.pack(side="left", padx=5)
        ttk.Label(q_row1, text="الكمية:", width=10).pack(side="left", padx=5)
        self.entry_q_qty = ttk.Entry(q_row1, width=8)
        self.entry_q_qty.insert(0, "1")
        self.entry_q_qty.pack(side="left", padx=5)

        q_row2 = ttk.Frame(quote_frame)
        q_row2.pack(fill="x", pady=4)
        ttk.Label(q_row2, text="السرعة (mm/min):", width=14).pack(side="left", padx=5)
        self.entry_q_speed = ttk.Entry(q_row2, width=10)
        self.entry_q_speed.insert(0, "1200")
        self.entry_q_speed.pack(side="left", padx=5)
        ttk.Label(q_row2, text="تكلفة الآلة/ساعة:", width=14).pack(side="left", padx=5)
        self.entry_q_machine = ttk.Entry(q_row2, width=10)
        self.entry_q_machine.insert(0, "120")
        self.entry_q_machine.pack(side="left", padx=5)
        ttk.Label(q_row2, text="ثمن المادة/قطعة:", width=14).pack(side="left", padx=5)
        self.entry_q_material = ttk.Entry(q_row2, width=10)
        self.entry_q_material.insert(0, "10")
        self.entry_q_material.pack(side="left", padx=5)

        q_row3 = ttk.Frame(quote_frame)
        q_row3.pack(fill="x", pady=4)
        ttk.Label(q_row3, text="هامش الربح %:", width=14).pack(side="left", padx=5)
        self.entry_q_margin = ttk.Entry(q_row3, width=10)
        self.entry_q_margin.insert(0, "30")
        self.entry_q_margin.pack(side="left", padx=5)
        ttk.Button(
            q_row3,
            text="احسب السعر المقترح",
            command=self._estimate_quote,
            style="Primary.TButton",
        ).pack(side="left", padx=8)

        self.label_quote_result = ttk.Label(
            quote_frame,
            text="",
            style="TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.label_quote_result.pack(anchor="w", padx=10, pady=(3, 8))

        # --- Sheet Planner ---
        sheet_frame = ttk.LabelFrame(body, text="📐 تخطيط الصفائح / Sheet Planner")
        sheet_frame.pack(fill="x", pady=(0, 10))

        s_row1 = ttk.Frame(sheet_frame)
        s_row1.pack(fill="x", pady=4)
        ttk.Label(s_row1, text="قطعة W (mm):", width=14).pack(side="left", padx=5)
        self.entry_part_w = ttk.Entry(s_row1, width=10)
        self.entry_part_w.pack(side="left", padx=5)
        ttk.Label(s_row1, text="قطعة H (mm):", width=14).pack(side="left", padx=5)
        self.entry_part_h = ttk.Entry(s_row1, width=10)
        self.entry_part_h.pack(side="left", padx=5)
        ttk.Label(s_row1, text="الكمية:", width=10).pack(side="left", padx=5)
        self.entry_part_qty = ttk.Entry(s_row1, width=8)
        self.entry_part_qty.insert(0, "1")
        self.entry_part_qty.pack(side="left", padx=5)

        s_row2 = ttk.Frame(sheet_frame)
        s_row2.pack(fill="x", pady=4)
        ttk.Label(s_row2, text="صفيحة W (mm):", width=14).pack(side="left", padx=5)
        self.entry_sheet_w = ttk.Entry(s_row2, width=10)
        self.entry_sheet_w.insert(0, "2440")
        self.entry_sheet_w.pack(side="left", padx=5)
        ttk.Label(s_row2, text="صفيحة H (mm):", width=14).pack(side="left", padx=5)
        self.entry_sheet_h = ttk.Entry(s_row2, width=10)
        self.entry_sheet_h.insert(0, "1220")
        self.entry_sheet_h.pack(side="left", padx=5)
        ttk.Button(
            s_row2,
            text="احسب الاستغلال",
            command=self._calc_sheet_usage,
            style="Outline.TButton",
        ).pack(side="left", padx=8)

        self.label_sheet_result = ttk.Label(
            sheet_frame,
            text="",
            style="TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.label_sheet_result.pack(anchor="w", padx=10, pady=(3, 8))

        # --- Workspace Shortcuts ---
        workspace_frame = ttk.LabelFrame(body, text="🗂️ اختصارات سريعة / Workspace Shortcuts")
        workspace_frame.pack(fill="x", pady=(0, 10))

        shortcuts = [
            ("📤 فتح exports", "exports"),
            ("📚 فتح docs", "docs"),
            ("🧠 فتح modules", "modules"),
            ("💾 فتح storage", "storage"),
        ]
        for title, folder in shortcuts:
            ttk.Button(
                workspace_frame,
                text=title,
                command=lambda p=folder: self._open_folder(p),
                style="Outline.TButton",
            ).pack(fill="x", padx=5, pady=2)

    def _convert_from_mm(self) -> None:
        try:
            val = float(self.entry_mm.get().strip())
            self.entry_cm.delete(0, tk.END)
            self.entry_cm.insert(0, f"{val / 10:.4f}")
            self.entry_inches.delete(0, tk.END)
            self.entry_inches.insert(0, f"{val / 25.4:.4f}")
        except ValueError:
            messagebox.showerror("خطأ", "أدخل رقماً صحيحاً في mm")

    def _convert_from_cm(self) -> None:
        try:
            val = float(self.entry_cm.get().strip())
            self.entry_mm.delete(0, tk.END)
            self.entry_mm.insert(0, f"{val * 10:.2f}")
            self.entry_inches.delete(0, tk.END)
            self.entry_inches.insert(0, f"{val / 2.54:.4f}")
        except ValueError:
            messagebox.showerror("خطأ", "أدخل رقماً صحيحاً في cm")

    def _convert_from_inches(self) -> None:
        try:
            val = float(self.entry_inches.get().strip())
            self.entry_mm.delete(0, tk.END)
            self.entry_mm.insert(0, f"{val * 25.4:.2f}")
            self.entry_cm.delete(0, tk.END)
            self.entry_cm.insert(0, f"{val * 2.54:.4f}")
        except ValueError:
            messagebox.showerror("خطأ", "أدخل رقماً صحيحاً في inches")

    def _calc_engraving_time(self) -> None:
        try:
            dist = float(self.entry_distance.get().strip())
            speed = float(self.entry_speed.get().strip())
            if speed <= 0:
                raise ValueError("السرعة يجب أن تكون أكبر من 0")
            minutes = dist / speed
            if minutes < 1:
                secs = int(minutes * 60)
                self.label_time_result.config(text=f"⏱️ الوقت التقريبي: {secs} ثانية")
            else:
                self.label_time_result.config(text=f"⏱️ الوقت التقريبي: {minutes:.2f} دقيقة ({int(minutes)} د {int((minutes % 1) * 60)} ث)")
        except ValueError as e:
            self.label_time_result.config(text="")
            messagebox.showerror("خطأ", str(e) if str(e) else "أدخل المسافة والسرعة (أرقام صحيحة)")

    def _backup_db(self) -> None:
        path = filedialog.asksaveasfilename(
            title="حفظ نسخة من قاعدة البيانات",
            defaultextension=".db",
            filetypes=(("SQLite DB", "*.db"), ("All files", "*.*")),
            initialfile=f"laser_app_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
        )
        if path:
            try:
                shutil.copy2(DB_NAME, path)
                messagebox.showinfo("نجاح", f"تم النسخ الاحتياطي إلى:\n{path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل النسخ:\n{e}")

    def _estimate_quote(self) -> None:
        try:
            width = float(self.entry_q_width.get().strip())
            height = float(self.entry_q_height.get().strip())
            qty = int(float(self.entry_q_qty.get().strip()))
            speed = float(self.entry_q_speed.get().strip())
            machine_cost_per_hour = float(self.entry_q_machine.get().strip())
            material_cost = float(self.entry_q_material.get().strip())
            margin_pct = float(self.entry_q_margin.get().strip())

            if width <= 0 or height <= 0 or qty <= 0 or speed <= 0:
                raise ValueError("كل القيم الأساسية خاصها تكون أكبر من صفر")

            perimeter_mm = 2 * (width + height)
            minutes_per_piece = perimeter_mm / speed
            machine_cost_per_piece = (minutes_per_piece / 60.0) * machine_cost_per_hour
            base_cost_piece = machine_cost_per_piece + material_cost
            final_price_piece = base_cost_piece * (1.0 + (margin_pct / 100.0))
            total = final_price_piece * qty

            self.label_quote_result.config(
                text=(
                    f"السعر/قطعة: {final_price_piece:.2f} | الإجمالي: {total:.2f} | "
                    f"الوقت/قطعة: {minutes_per_piece:.2f} دقيقة"
                )
            )
        except ValueError as e:
            self.label_quote_result.config(text="")
            messagebox.showerror("خطأ", str(e) if str(e) else "تحقق من قيم التسعير")

    def _calc_sheet_usage(self) -> None:
        try:
            part_w = float(self.entry_part_w.get().strip())
            part_h = float(self.entry_part_h.get().strip())
            qty = int(float(self.entry_part_qty.get().strip()))
            sheet_w = float(self.entry_sheet_w.get().strip())
            sheet_h = float(self.entry_sheet_h.get().strip())

            if min(part_w, part_h, sheet_w, sheet_h) <= 0 or qty <= 0:
                raise ValueError("كل القيم خاصها تكون أكبر من صفر")

            normal_fit = int(sheet_w // part_w) * int(sheet_h // part_h)
            rotated_fit = int(sheet_w // part_h) * int(sheet_h // part_w)
            per_sheet = max(normal_fit, rotated_fit)

            if per_sheet <= 0:
                self.label_sheet_result.config(text="لا يمكن وضع القطعة داخل الصفيحة بهذ المقاسات")
                return

            sheets_needed = math.ceil(qty / per_sheet)
            self.label_sheet_result.config(
                text=f"قطع/صفيحة: {per_sheet} | صفائح مطلوبة: {sheets_needed}"
            )
        except ValueError as e:
            self.label_sheet_result.config(text="")
            messagebox.showerror("خطأ", str(e) if str(e) else "تحقق من القيم")

    def _open_folder(self, folder_name: str) -> None:
        target = os.path.join(os.getcwd(), folder_name)
        if not os.path.isdir(target):
            messagebox.showerror("خطأ", f"المجلد غير موجود:\n{target}")
            return
        try:
            if hasattr(os, "startfile"):
                os.startfile(target)  # type: ignore[attr-defined]
            else:
                messagebox.showinfo("معلومة", target)
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر فتح المجلد:\n{e}")


class LanguageFrame(BaseFrame):
    """Language selection frame."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.lang_manager = app.lang_manager
        self._build()
    
    def _build(self) -> None:
        """Build language selection interface."""
        lang = self.lang_manager
        header = ttk.Frame(self, style="Card.TFrame")
        header.pack(fill="x", padx=12, pady=(8, 20))
        ttk.Label(header, text=f"🌐 {lang.get('language')}", style="Heading.TLabel").pack(side="left", padx=16)
        
        # Language container
        lang_container = ttk.Frame(self)
        lang_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Language selection
        lang_frame = ttk.LabelFrame(lang_container, text="اختر اللغة / Choose Language", padding=20)
        lang_frame.pack(fill="x", pady=10)
        
        ttk.Label(lang_frame, text="Current / الحالي:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=10)
        
        lang_var = tk.StringVar(value=self.lang_manager.get_language())
        lang_frame_btns = ttk.Frame(lang_frame)
        lang_frame_btns.pack(fill="x", pady=10)
        
        # French
        ttk.Radiobutton(
            lang_frame_btns,
            text="🇫🇷 Français (French)",
            variable=lang_var,
            value="fr",
            command=lambda: self._change_language("fr"),
        ).pack(side="left", padx=15)
        
        # English
        ttk.Radiobutton(
            lang_frame_btns,
            text="🇬🇧 English",
            variable=lang_var,
            value="en",
            command=lambda: self._change_language("en"),
        ).pack(side="left", padx=15)
        
        # Arabic
        ttk.Radiobutton(
            lang_frame_btns,
            text="🇲🇦 العربية (Arabic)",
            variable=lang_var,
            value="ar",
            command=lambda: self._change_language("ar"),
        ).pack(side="left", padx=15)
        
        # Note - changes apply immediately
        note = ttk.Label(
            lang_container,
            text=self.lang_manager.get("lang_note"),
            style="Subtle.TLabel",
            justify="center",
        )
        note.pack(pady=20)
    
    def _change_language(self, lang: str) -> None:
        """Change language and refresh UI."""
        self.lang_manager.set_language(lang)
        # Refresh entire application UI
        self.app.refresh_language()


class SettingsFrame(BaseFrame):
    """Settings page for theme, layout, and UI style configuration."""
    
    def __init__(self, parent: tk.Widget, app: "LaserApp"):
        super().__init__(parent, app)
        self.ui_engine = app.ui_engine
        self._build()
    
    def _build(self) -> None:
        """Build settings interface."""
        lang = self.app.lang_manager
        header = ttk.Frame(self, style="Card.TFrame")
        header.pack(fill="x", padx=12, pady=(8, 20))
        ttk.Label(header, text=f"⚙️ {lang.get('settings')}", style="Heading.TLabel").pack(side="left", padx=16)
        
        # Settings container
        settings_container = ttk.Frame(self)
        settings_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Theme Section
        theme_frame = ttk.LabelFrame(settings_container, text=lang.get("theme"), padding=15)
        theme_frame.pack(fill="x", pady=10)
        
        ttk.Label(theme_frame, text=f"{lang.get('appearance')}:").pack(anchor="w", pady=5)
        theme_var = tk.StringVar(value=self.ui_engine.current_theme)
        theme_frame_btns = ttk.Frame(theme_frame)
        theme_frame_btns.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            theme_frame_btns,
            text=f"☀️ {lang.get('light')}",
            variable=theme_var,
            value="light",
            command=lambda: self._change_theme("light"),
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            theme_frame_btns,
            text=f"🌙 {lang.get('dark')}",
            variable=theme_var,
            value="dark",
            command=lambda: self._change_theme("dark"),
        ).pack(side="left", padx=10)

        ttk.Radiobutton(
            theme_frame_btns,
            text="🏭 Industrial",
            variable=theme_var,
            value="industrial",
            command=lambda: self._change_theme("industrial"),
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            theme_frame_btns,
            text="🏢 ERP Pro",
            variable=theme_var,
            value="erp_pro",
            command=lambda: self._change_theme("erp_pro"),
        ).pack(side="left", padx=10)
        
        # Layout Section
        layout_frame = ttk.LabelFrame(settings_container, text="Navigation Layout", padding=15)
        layout_frame.pack(fill="x", pady=10)
        
        ttk.Label(layout_frame, text="Menu Style:").pack(anchor="w", pady=5)
        layout_var = tk.StringVar(value=self.ui_engine.current_layout)
        layout_frame_btns = ttk.Frame(layout_frame)
        layout_frame_btns.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            layout_frame_btns,
            text="Sidebar Only",
            variable=layout_var,
            value=UIEngine.LAYOUT_SIDEBAR,
            command=lambda: self._change_layout(UIEngine.LAYOUT_SIDEBAR),
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            layout_frame_btns,
            text="Top Menu Only",
            variable=layout_var,
            value=UIEngine.LAYOUT_TOPBAR,
            command=lambda: self._change_layout(UIEngine.LAYOUT_TOPBAR),
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            layout_frame_btns,
            text="Both",
            variable=layout_var,
            value=UIEngine.LAYOUT_BOTH,
            command=lambda: self._change_layout(UIEngine.LAYOUT_BOTH),
        ).pack(side="left", padx=10)
        
        # Top Menu Mode Section
        topmenu_frame = ttk.LabelFrame(settings_container, text="Top Menu Mode", padding=15)
        topmenu_frame.pack(fill="x", pady=10)
        
        ttk.Label(topmenu_frame, text="Top Menu Style:").pack(anchor="w", pady=5)
        topmenu_var = tk.StringVar(value="simple")
        topmenu_frame_btns = ttk.Frame(topmenu_frame)
        topmenu_frame_btns.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            topmenu_frame_btns,
            text="Simple",
            variable=topmenu_var,
            value="simple",
            command=lambda: self._change_topmenu_mode("simple"),
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            topmenu_frame_btns,
            text="Engineering",
            variable=topmenu_var,
            value="engineering",
            command=lambda: self._change_topmenu_mode("engineering"),
        ).pack(side="left", padx=10)
        
        # UI Style Section
        style_frame = ttk.LabelFrame(settings_container, text="UI Style", padding=15)
        style_frame.pack(fill="x", pady=10)
        
        ttk.Label(style_frame, text="Interface Style:").pack(anchor="w", pady=5)
        style_var = tk.StringVar(value=self.ui_engine.current_ui_style)
        style_frame_btns = ttk.Frame(style_frame)
        style_frame_btns.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            style_frame_btns,
            text="Modern",
            variable=style_var,
            value=UIEngine.STYLE_MODERN,
            command=lambda: self._change_ui_style(UIEngine.STYLE_MODERN),
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            style_frame_btns,
            text="Flutter",
            variable=style_var,
            value=UIEngine.STYLE_FLUTTER,
            command=lambda: self._change_ui_style(UIEngine.STYLE_FLUTTER),
        ).pack(side="left", padx=10)
    
    def _change_theme(self, theme: str) -> None:
        """Change theme and refresh UI."""
        self.ui_engine.set_theme(theme)
        self.app.refresh_ui()
    
    def _change_layout(self, layout: str) -> None:
        """Change layout mode."""
        self.ui_engine.set_layout(layout)
        self.app.refresh_layout()
    
    def _change_topmenu_mode(self, mode: str) -> None:
        """Change top menu mode."""
        if hasattr(self.app, "top_menu"):
            self.app.top_menu.set_mode(mode)
    
    def _change_ui_style(self, style: str) -> None:
        """Change UI style."""
        self.ui_engine.set_ui_style(style)
        self.app.refresh_ui()


class LaserApp(tk.Tk):
    """Main Tk application with professional UI system."""

    def __init__(self):
        super().__init__()
        self.geometry("1366x820")
        self.minsize(1180, 700)

        # Initialize UI Engine
        self.ui_engine = UIEngine(self)
        self.ui_engine.set_theme("erp_pro")
        self.ui_engine.set_layout(UIEngine.LAYOUT_TOPBAR)
        
        # Initialize Language Manager
        self.lang_manager = LanguageManager(default_lang="ar")
        self.title(f"Laser Pro - {self.lang_manager.get('my_studio')}")
        
        self.db = LaserDB()

        # Main layout container
        self.main_container = ttk.Frame(self, style="TFrame")
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar (Full)
        self.sidebar = SidebarFull(self.main_container, self, self.ui_engine)
        if self.ui_engine.current_layout != UIEngine.LAYOUT_TOPBAR:
            self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.configure(width=220)
        
        # Content area (right side)
        self.content_area = ttk.Frame(self.main_container, style="Panel.TFrame")
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Top Menu Bar
        self.top_menu = TopMenuBar(self.content_area, self, self.ui_engine, mode="simple")
        self.top_menu.pack(fill="x", padx=4, pady=(4, 2))

        # Top tabs (primary navigation in topbar layout)
        self.top_tabs = TopTabsBar(self.content_area, self, self.ui_engine)
        self.top_tabs.pack(fill="x", padx=4, pady=(0, 4))
        
        # Frames container
        self.frames_container = ttk.Frame(self.content_area, style="Card.TFrame")
        self.frames_container.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        
        # Initialize all frames
        self.frames = {}
        for F in (MyStudioFrame, HomeFrame, JobsFrame, NewJobFrame, ModulesFrame, VectorCenterFrame, ToolsFrame, LanguageFrame, SettingsFrame):
            frame = F(self.frames_container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Frame titles mapping
        self.frame_titles = {
            "MyStudioFrame": "Dashboard",
            "HomeFrame": "Dashboard",
            "JobsFrame": "Projects",
            "NewJobFrame": "New Project",
            "VectorCenterFrame": "Vector Center",
            "ToolsFrame": "Tools",
            "ModulesFrame": "Modules",
            "LanguageFrame": "Language",
            "SettingsFrame": "Settings",
        }

        self.show_frame("MyStudioFrame")
        self.refresh_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, name: str) -> None:
        """Show frame and update UI."""
        if name not in self.frames:
            return
        
        frame = self.frames[name]
        frame.tkraise()
        
        # Update top menu title
        title = self.frame_titles.get(name, name)
        if hasattr(self, "top_menu"):
            self.top_menu.update_title(title)
        
        # Update sidebar active state
        if hasattr(self, "sidebar"):
            self.sidebar._set_active(name)
        if hasattr(self, "top_tabs"):
            self.top_tabs.set_active(name)
        
        # Refresh frame if needed
        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except (TypeError, AttributeError):
                pass

    def refresh_ui(self) -> None:
        """Refresh entire UI after theme/style change."""
        self.ui_engine._apply_theme()
        # Force update all widgets
        self.update_idletasks()

    def refresh_layout(self) -> None:
        """Refresh layout after layout mode change."""
        layout = self.ui_engine.current_layout
        if layout == UIEngine.LAYOUT_TOPBAR:
            if self.sidebar.winfo_ismapped():
                self.sidebar.pack_forget()
        elif layout == UIEngine.LAYOUT_SIDEBAR:
            if not self.sidebar.winfo_ismapped():
                self.sidebar.pack(side="left", fill="y", padx=0, pady=0, before=self.content_area)
            if hasattr(self, "top_tabs") and self.top_tabs.winfo_ismapped():
                self.top_tabs.pack_forget()
        else:
            if not self.sidebar.winfo_ismapped():
                self.sidebar.pack(side="left", fill="y", padx=0, pady=0, before=self.content_area)
            if hasattr(self, "top_tabs") and not self.top_tabs.winfo_ismapped():
                self.top_tabs.pack(fill="x", padx=0, pady=0, after=self.top_menu)
        if layout == UIEngine.LAYOUT_TOPBAR and hasattr(self, "top_tabs") and not self.top_tabs.winfo_ismapped():
            self.top_tabs.pack(fill="x", padx=0, pady=0, after=self.top_menu)

    def refresh_language(self) -> None:
        """Refresh entire UI after language change."""
        # Refresh Sidebar
        if hasattr(self, "sidebar"):
            self.sidebar._build_nav_buttons()
        
        # Refresh Top Menu
        if hasattr(self, "top_menu"):
            current_mode = self.top_menu.mode
            self.top_menu.set_mode(current_mode)
        if hasattr(self, "top_tabs"):
            self.top_tabs.refresh_labels()
        
        # Refresh current frame
        current_frame_name = None
        for name, frame in self.frames.items():
            if frame.winfo_viewable():
                current_frame_name = name
                break
        
        if current_frame_name:
            self.show_frame(current_frame_name)
        
        # Update frame titles
        lang = self.lang_manager
        self.frame_titles = {
            "MyStudioFrame": lang.get("dashboard"),
            "HomeFrame": lang.get("dashboard"),
            "JobsFrame": lang.get("projects"),
            "NewJobFrame": lang.get("new_project"),
            "VectorCenterFrame": lang.get("vector_center"),
            "ToolsFrame": lang.get("tools"),
            "ModulesFrame": lang.get("modules"),
            "LanguageFrame": lang.get("language"),
            "SettingsFrame": lang.get("settings"),
        }
        # Update window title
        self.title(f"Laser Pro - {lang.get('my_studio')}")

    def on_close(self) -> None:
        """Handle window close."""
        lang = self.lang_manager
        if messagebox.askokcancel(lang.get("exit"), lang.get("exit_confirm")):
            self.db.close()
            self.destroy()


if __name__ == "__main__":
    app = LaserApp()
    app.mainloop()
