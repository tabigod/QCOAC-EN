"""
YVR助手 - 桌面端主窗口
左侧导航栏 + 右侧内容区域布局
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

from desktop.ui.styles import *
from desktop.ui.pages.device_info import DeviceInfoPage
from desktop.ui.pages.install_game import InstallGamePage
from desktop.ui.pages.file_manager import FileManagerPage
from desktop.ui.pages.root_page import RootPage
from desktop.ui.pages.vr_screen import VRScreenPage
from desktop.ui.pages.adb_commands import ADBCommandsPage


class SidebarButton(QPushButton):
    """左侧导航栏按钮"""
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self._active = False
        self._icon_text = icon_text
        self.setText(f"  {icon_text}  {text}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._update_style()

    def set_active(self, active):
        self._active = active
        self.setChecked(active)
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {PRIMARY}, stop:1 rgba(108, 92, 231, 0.3));
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    text-align: left;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: 10px;
                    padding: 10px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: rgba(108, 92, 231, 0.1);
                    color: {TEXT_PRIMARY};
                }}
            """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YVR助手")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 820)

        # 应用全局样式
        self.setStyleSheet(get_stylesheet())

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========== 左侧边栏 ==========
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # ========== 右侧内容区 ==========
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {BG_DARK};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet("background: transparent;")

        # 创建页面
        self.pages = {
            "device_info": DeviceInfoPage(),
            "install_game": InstallGamePage(),
            "file_manager": FileManagerPage(),
            "root": RootPage(),
            "vr_screen": VRScreenPage(),
            "adb_commands": ADBCommandsPage(),
        }
        for p in self.pages.values():
            self.stacked.addWidget(p)

        content_layout.addWidget(self.stacked)
        main_layout.addWidget(content_area)

        # 默认显示设备信息
        self._switch_page("device_info")
        self.sidebar_buttons["device_info"].set_active(True)

    def _create_sidebar(self):
        """创建左侧导航栏"""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border-right: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(4)

        # ---------- Logo / 标题 ----------
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 16)
        logo_layout.setSpacing(4)

        # Logo 图标
        logo_icon = QLabel("YVR")
        logo_icon.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 900;
            color: {PRIMARY};
            background: transparent;
            letter-spacing: 2px;
        """)
        logo_icon.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_layout.addWidget(logo_icon)

        # 副标题
        logo_sub = QLabel("助手")
        logo_sub.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {TEXT_SECONDARY};
            background: transparent;
        """)
        logo_layout.addWidget(logo_sub)

        layout.addWidget(logo_container)

        # ---------- 分割线 ----------
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        layout.addWidget(sep)

        layout.addSpacing(12)

        # ---------- 导航菜单 ----------
        nav_label = QLabel("主要功能")
        nav_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 1px;
            background: transparent;
            padding: 0 8px;
            margin-bottom: 4px;
        """)
        layout.addWidget(nav_label)

        # 菜单项定义
        menu_items = [
            ("device_info", "设备信息", "📱"),
            ("install_game", "安装游戏", "🎮"),
            ("file_manager", "文件管理", "📁"),
            ("root", "Root", "🔧"),
            ("vr_screen", "VR投屏", "📺"),
            ("adb_commands", "ADB命令", "💻"),
        ]

        self.sidebar_buttons = {}

        for key, name, icon in menu_items:
            btn = SidebarButton(name, icon)
            btn.clicked.connect(lambda checked, k=key: self._switch_page(k))
            self.sidebar_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # ---------- 底部状态 ----------
        bottom_sep = QFrame()
        bottom_sep.setFrameShape(QFrame.HLine)
        bottom_sep.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        layout.addWidget(bottom_sep)

        layout.addSpacing(12)

        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"""
            font-size: 11px;
            color: {TEXT_MUTED};
            background: transparent;
            padding: 0 8px;
        """)
        layout.addWidget(version_label)

        status_label = QLabel("需要连接设备")
        status_label.setStyleSheet(f"""
            font-size: 11px;
            color: {WARNING};
            background: transparent;
            padding: 0 8px;
        """)
        layout.addWidget(status_label)

        return sidebar

    def _switch_page(self, page_key):
        """切换页面"""
        # 更新按钮状态
        for key, btn in self.sidebar_buttons.items():
            btn.set_active(key == page_key)

        # 切换内容
        if page_key in self.pages:
            self.stacked.setCurrentWidget(self.pages[page_key])