"""
YVR助手 - 主应用框架
整合侧边栏导航 + 页面路由 + 设备连接管理
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS
from ui.sidebar import Sidebar
from core.adb_manager import ADBManager

from ui.pages.device_info import DeviceInfoPage
from ui.pages.install_game import InstallGamePage
from ui.pages.file_manager import FileManagerPage
from ui.pages.root_tool import RootToolPage
from ui.pages.vr_screen import VRScreenPage
from ui.pages.adb_command import ADBCommandPage


class YVRAssistant(ctk.CTk):
    """YVR助手主应用"""

    def __init__(self):
        super().__init__()

        self.title("YVR助手")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 窗口居中
        self._center_window()

        # ADB 管理器
        self.adb = ADBManager()
        self.adb.set_status_callback(self._on_connection_change)

        # 页面缓存
        self._pages = {}
        self._current_page = None

        # 构建 UI
        self._build_ui()

        # 默认显示设备信息页
        self._show_page("设备信息")

        # 启动时检测 ADB
        self.after(500, self._init_adb_check)

    def _center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """构建主界面"""
        # 配置网格
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 左侧导航栏
        self.sidebar = Sidebar(self, on_navigate=self._show_page, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # 右侧内容区
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # 顶部状态栏
        self._build_top_bar()

    def _build_top_bar(self):
        """顶部状态栏"""
        top_bar = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_header"], height=50, corner_radius=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        # 连接状态
        self.connection_dot = ctk.CTkLabel(
            top_bar, text="●", font=("Segoe UI", 14, "bold"),
            text_color=COLORS["danger"], width=20
        )
        self.connection_dot.pack(side="left", padx=(20, 5), pady=12)

        self.connection_label = ctk.CTkLabel(
            top_bar, text="设备未连接",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.connection_label.pack(side="left", pady=12)

        # 刷新连接按钮
        self.refresh_conn_btn = ctk.CTkButton(
            top_bar, text="刷新连接", font=FONTS["small"],
            fg_color=COLORS["bg_card"], hover_color=COLORS["accent"],
            corner_radius=6, height=28, width=80,
            command=self._refresh_connection
        )
        self.refresh_conn_btn.pack(side="right", padx=(0, 20), pady=10)

        # ADB 状态
        self.adb_status_label = ctk.CTkLabel(
            top_bar, text="ADB: 检测中...", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self.adb_status_label.pack(side="right", padx=(0, 15), pady=12)

        # 分隔线
        sep = ctk.CTkFrame(self.content_frame, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x")

    def _show_page(self, name):
        """切换页面"""
        # 销毁旧页面
        if self._current_page:
            self._current_page.pack_forget()

        # 创建或获取页面
        if name not in self._pages:
            page = self._create_page(name)
            self._pages[name] = page

        page = self._pages[name]
        page.pack(in_=self.content_frame, fill="both", expand=True, side="top", anchor="n")
        self._current_page = page

        # 高亮侧边栏
        self.sidebar.set_active(name)

        # 通知页面
        if hasattr(page, "on_show"):
            page.on_show()

    def _create_page(self, name):
        """创建对应页面"""
        pages = {
            "设备信息": DeviceInfoPage,
            "安装游戏": InstallGamePage,
            "文件管理": FileManagerPage,
            "Root": RootToolPage,
            "VR投屏": VRScreenPage,
            "ADB命令": ADBCommandPage,
        }
        page_cls = pages.get(name)
        if page_cls:
            return page_cls(self.content_frame, self.adb)
        return None

    def _on_connection_change(self, connected, device_model):
        """设备连接状态变化回调"""
        if connected:
            self.connection_dot.configure(text_color=COLORS["success"])
            self.connection_label.configure(text=f"已连接 - {device_model}")
            self.sidebar.update_status(True, device_model)
        else:
            self.connection_dot.configure(text_color=COLORS["danger"])
            self.connection_label.configure(text="设备未连接")
            self.sidebar.update_status(False)

    def _init_adb_check(self):
        """初始化时检查 ADB"""
        adb_ok = self.adb.check_adb()
        if adb_ok:
            self.adb_status_label.configure(text="ADB: 就绪", text_color=COLORS["success"])
        else:
            self.adb_status_label.configure(text="ADB: 未找到", text_color=COLORS["danger"])

        # 自动检测设备
        self._refresh_connection()

    def _refresh_connection(self):
        """手动刷新连接"""
        self.refresh_conn_btn.configure(state="disabled", text="检测中...")
        self.adb_status_label.configure(text="ADB: 扫描中...", text_color=COLORS["info"])

        def _do_refresh():
            connected, msg = self.adb.refresh_connection()
            self.after(0, lambda: self._on_refresh_done(connected, msg))

        import threading
        threading.Thread(target=_do_refresh, daemon=True).start()

    def _on_refresh_done(self, connected, msg):
        self.refresh_conn_btn.configure(state="normal", text="刷新连接")
        adb_ok = self.adb.check_adb()
        self.adb_status_label.configure(
            text="ADB: 就绪" if adb_ok else "ADB: 未找到",
            text_color=COLORS["success"] if adb_ok else COLORS["danger"]
        )