"""
YVR助手 - 安装游戏页面
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from ui.theme import COLORS, FONTS


class InstallGamePage(ctk.CTkFrame):
    """安装游戏页面 - APK 安装管理"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._apk_queue = []
        self._installing = False
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="安装游戏", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="选择 APK 文件安装到设备",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 0))

        # 提示
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再使用此功能",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=15)

        # 拖拽区域
        self.drop_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"], corner_radius=12,
            border_width=2, border_color=COLORS["border"]
        )
        self.drop_frame.pack(fill="x", padx=30, pady=(0, 15))

        drop_inner = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        drop_inner.pack(pady=40, padx=40)

        ctk.CTkLabel(
            drop_inner, text="📦", font=("Segoe UI Emoji", 40),
        ).pack()

        ctk.CTkLabel(
            drop_inner, text="将 APK 文件拖拽到此处",
            font=FONTS["subtitle"], text_color=COLORS["text_secondary"]
        ).pack(pady=(5, 5))

        ctk.CTkLabel(
            drop_inner, text="或点击下方按钮选择文件",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        ).pack()

        select_btn = ctk.CTkButton(
            drop_inner, text="选择 APK 文件", font=FONTS["body_bold"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=8, width=140, height=36,
            command=self._select_apk
        )
        select_btn.pack(pady=(15, 0))

        # 安装列表
        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.pack(fill="x", padx=30, pady=(0, 5))

        ctk.CTkLabel(
            list_header, text="安装队列", font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        self.clear_btn = ctk.CTkButton(
            list_header, text="清空队列", font=FONTS["small"],
            fg_color=COLORS["bg_card"], hover_color=COLORS["danger"],
            corner_radius=6, width=80, height=28,
            command=self._clear_queue
        )
        self.clear_btn.pack(side="right", padx=(5, 0))

        self.install_all_btn = ctk.CTkButton(
            list_header, text="全部安装", font=FONTS["small"],
            fg_color=COLORS["success"], hover_color="#00B87A",
            corner_radius=6, width=80, height=28,
            command=self._install_all
        )
        self.install_all_btn.pack(side="right")

        # 队列列表
        self.queue_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border_light"],
            scrollbar_button_hover_color=COLORS["text_muted"],
        )
        self.queue_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.empty_label = ctk.CTkLabel(
            self.queue_container, text="暂无待安装的 APK 文件",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        )
        self.empty_label.pack(pady=30)

        self._queue_widgets = []

    def _select_apk(self):
        files = filedialog.askopenfilenames(
            title="选择 APK 文件",
            filetypes=[("APK 文件", "*.apk"), ("所有文件", "*.*")]
        )
        for f in files:
            if f not in self._apk_queue:
                self._apk_queue.append(f)
        self._refresh_queue()

    def _refresh_queue(self):
        """刷新队列显示"""
        for w in self._queue_widgets:
            w.destroy()
        self._queue_widgets.clear()

        if not self._apk_queue:
            self.empty_label.pack(pady=30)
            self.install_all_btn.configure(state="disabled")
            self.clear_btn.configure(state="disabled")
            return

        self.empty_label.pack_forget()
        self.install_all_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")

        for i, apk_path in enumerate(self._apk_queue):
            self._add_queue_item(i, apk_path)

    def _add_queue_item(self, index, apk_path):
        frame = ctk.CTkFrame(self.queue_container, fg_color=COLORS["bg_card"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 6))

        name = os.path.basename(apk_path)
        size = os.path.getsize(apk_path) / (1024 * 1024)

        ctk.CTkLabel(
            frame, text=f"  {index + 1}.", font=FONTS["body_bold"],
            text_color=COLORS["accent_light"], width=30
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            frame, text=name, font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(5, 10))

        ctk.CTkLabel(
            frame, text=f"{size:.1f} MB", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 10))

        status_label = ctk.CTkLabel(
            frame, text="等待安装", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        status_label.pack(side="right", padx=(0, 10))

        remove_btn = ctk.CTkButton(
            frame, text="✕", font=FONTS["body_bold"],
            fg_color="transparent", hover_color=COLORS["danger"],
            corner_radius=6, width=30, height=30,
            text_color=COLORS["text_muted"],
            command=lambda idx=index: self._remove_apk(idx)
        )
        remove_btn.pack(side="right", padx=(0, 5))

        frame.status_label = status_label
        frame.apk_path = apk_path
        self._queue_widgets.append(frame)

    def _remove_apk(self, index):
        if 0 <= index < len(self._apk_queue):
            self._apk_queue.pop(index)
            self._refresh_queue()

    def _clear_queue(self):
        self._apk_queue.clear()
        self._refresh_queue()

    def _install_all(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return
        if not self._apk_queue:
            return
        self._installing = True
        self.install_all_btn.configure(state="disabled", text="安装中...")
        self._install_next(0)

    def _install_next(self, index):
        if index >= len(self._apk_queue):
            self._installing = False
            self.install_all_btn.configure(state="normal", text="全部安装")
            self.tip_label.configure(text="✅ 全部安装完成！")
            self._apk_queue.clear()
            self._refresh_queue()
            return

        apk_path = self._apk_queue[index]
        name = os.path.basename(apk_path)

        if index < len(self._queue_widgets):
            self._queue_widgets[index].status_label.configure(
                text="正在安装...", text_color=COLORS["info"]
            )

        def on_done(code, out, err):
            self.after(0, lambda: self._on_install_done(index, code, out, err))

        self.adb.install_apk(apk_path, on_done)

    def _on_install_done(self, index, code, out, err):
        if index < len(self._queue_widgets):
            if code == 0:
                self._queue_widgets[index].status_label.configure(
                    text="✅ 完成", text_color=COLORS["success"]
                )
            else:
                self._queue_widgets[index].status_label.configure(
                    text=f"❌ 失败", text_color=COLORS["danger"]
                )
        self._install_next(index + 1)

    def on_show(self):
        if self.adb.is_connected:
            self.tip_label.configure(text="✅ 设备已连接，可以安装游戏")
        else:
            self.tip_label.configure(text="⚠️ 请先连接设备后再使用此功能")