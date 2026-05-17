# LaserFlow - Smart Laser/CNC Workshop Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.11.1-00ACC1?style=flat&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

</div>

---

## 📋 Description

**LaserFlow** is a comprehensive desktop application for managing CNC and Laser cutting workshops. It provides complete business management solutions including job tracking, client management, inventory, invoicing, and point of sale.

LaserFlow هو تطبيق سطح مكتب شامل لإدارة ورش قطع CNC والليزر. يوفر حلولاً كاملة لإدارة الأعمال والعملاء والمخزون والفواتير ونقطة البيع.

---

## 🚀 Features

### Core Features
- 📊 **Dashboard** - Real-time business metrics and KPIs
- 👥 **Client Management** - Track clients, contacts, and history
- 📝 **Quotes & Invoices** - Create and manage quotes/invoices
- 📦 **Stock & Inventory** - Material tracking and management
- 💰 **Sales & Purchases** - Complete financial tracking
- 🏪 **Point of Sale** - Quick sale processing
- 🔔 **Notifications** - Real-time alerts and updates
- ⚙️ **Settings** - Customizable application settings
- ℹ️ **About** - Application information

### Additional Features
- 🎨 Modern Dark/Light Theme support
- 🌐 Bilingual Interface (English/Arabic)
- 📈 Financial Reports
- 🔒 Secure Data Storage (SQLite)
- 🎯 Job Management for CNC/Laser operations

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.14+ |
| **GUI Framework** | PySide6 (Qt for Python) |
| **Database** | SQLite |
| **Design** | Custom QSS/CSS Styling |
| **Platform** | Windows |

---

## 📁 Project Structure

```
Laser-CNC-Business-App/
├── main_pyside6.py          # Main entry point
├── ui/                      # UI components
│   ├── pages/               # Application pages
│   ├── components/          # Reusable components
│   ├── router.py            # Page navigation
│   └── design_system.qss    # Theme styling
├── core/                   # Core functionality
├── services/               # Business logic
├── models/                 # Data models
├── utils/                  # Utilities
└── database.py             # Database management
```

---

## ⚡ Installation

### Prerequisites
- Python 3.8 or higher
- Windows OS

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/zougar99/Laser-CNC-Business-App.git
cd Laser-CNC-Business-App
```

2. **Create virtual environment** (optional but recommended)
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install PySide6 pillow numpy scipy shapely ezdxf reportlab
```

4. **Run the application**
```bash
python main_pyside6.py
```

---

## 📸 Screenshots

| Dashboard | Clients | Invoices |
|-----------|---------|----------|
| ![Dashboard](https://via.placeholder.com/400x300?text=Dashboard) | ![Clients](https://via.placeholder.com/400x300?text=Clients) | ![Invoices](https://via.placeholder.com/400x300?text=Invoices) |

---

## 🎯 Usage

1. Launch the application
2. Navigate using the sidebar
3. Add clients and create quotes
4. Track inventory and sales
5. Generate invoices and reports

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**WerList99** - [GitHub](https://github.com/zougar99)

- 🔧 Python Desktop App Developer
- 🦊 Firefox Extension Creator  
- ✍️ Tech Blogger

**Connect:**
- Telegram: [@werlist99](https://t.me/werlist99)
- Blog: [werlist99.blogspot.com](https://werlist99.blogspot.com)

---

## 🙏 Acknowledgments

- PySide6 team for the amazing Qt Python bindings
- Qt Company for the Qt framework
- Open source community for various libraries used

---

<div align="center">

**⭐ Star this project if you find it useful!**

Made with ❤️ by [WerList99](https://github.com/zougar99)

</div>