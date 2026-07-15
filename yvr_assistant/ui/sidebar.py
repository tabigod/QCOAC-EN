"""
YVR助手 - 侧边栏导航组件
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS


class Sidebar(ctk.CTkFrame):
    """左侧导航栏"""

    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_sidebar"], corner_radius=0, **kwargs)

        self.on_navigate = on_navigate
        self._buttons = {}
        self._active_btn = None

        self._build()

    def _build(self):
        # Logo 区域
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=0, pady=(25, 10))
        logo_frame.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="YVR 助手",
            font=("Microsoft YaHei UI", 22, "bold"),
            text_color=COLORS["accent_light"],
        )
        self.logo_label.pack(pady=(10, 0))

        version_label = ctk.CTkLabel(
            logo_frame,
            text="v1.0.0",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        version_label.pack(pady=(0, 5))

        # 分割线
        self._separator()

        # 导航菜单
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="both", expand=True, padx=12, pady=(10, 0))

        nav_items = [
            ("设备信息", "📱"),
            ("安装游戏", "🎮"),
            ("文件管理", "📂"),
            ("Root", "🛡️"),
            ("VR投屏", "🖥️"),
            ("ADB命令", "⌨️"),
        ]

        for name, icon in nav_items:
            self._add_nav_button(name, icon)

        # 底部区域
        self._separator()

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=12, pady=(10, 20))

        self.status_indicator = ctk.CTkLabel(
            bottom_frame,
            text="● 未连接",
            font=FONTS["small"],
            text_color=COLORS["danger"],
        )
        self.status_indicator.pack(pady=(5, 10))

    def _separator(self):
        sep = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=5)

    def _add_nav_button(self, name, icon):
        btn = ctk.CTkButton(
            self.nav_frame,
            text=f"  {icon}  {name}",
            font=FONTS["sidebar"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=10,
            height=44,
            anchor="w",
            command=lambda n=name: self._on_click(n),
        )
        btn.pack(fill="x", pady=3)
        self._buttons[name] = btn

    def _on_click(self, name):
        self.set_active(name)
        self.on_navigate(name)

    def set_active(self, name):
        """高亮当前选中的按钮"""
        if self._active_btn:
            self._active_btn.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
            )

        btn = self._buttons.get(name)
        if btn:
            btn.configure(
                fg_color=COLORS["accent"],
                text_color="#FFFFFF",
            )
            self._active_btn = btn

    def update_status(self, connected, device_model=""):
        """更新连接状态"""
        if connected:
            self.status_indicator.configure(
                text=f"● 已连接 - {device_model}",
                text_color=COLORS["success"],
            )
        else:
            self.status_indicator.configure(
                text="● 未连接",
                text_color=COLORS["danger"],
            )