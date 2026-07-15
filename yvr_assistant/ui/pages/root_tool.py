"""
YVR助手 - Root 工具页面
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS


class RootToolPage(ctk.CTkFrame):
    """Root 工具页面 - ADB Root 权限管理"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="Root 工具", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="管理设备 Root 权限",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 0))

        # 提示
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再使用 Root 工具",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=15)

        # 内容区域
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Root 状态卡片
        status_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        status_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            status_card, text="Root 状态", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        status_inner = ctk.CTkFrame(status_card, fg_color=COLORS["bg_input"], corner_radius=8)
        status_inner.pack(fill="x", padx=20, pady=(0, 15))

        self.status_value = ctk.CTkLabel(
            status_inner, text="未检测", font=FONTS["subtitle"],
            text_color=COLORS["text_muted"]
        )
        self.status_value.pack(pady=15)

        # Root 操作按钮
        action_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        action_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            action_card, text="Root 操作", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        btn_frame = ctk.CTkFrame(action_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.root_btn = ctk.CTkButton(
            btn_frame, text="获取 Root 权限", font=FONTS["body_bold"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=8, height=42,
            command=self._request_root
        )
        self.root_btn.pack(side="left", padx=(0, 10))

        self.remount_btn = ctk.CTkButton(
            btn_frame, text="重新挂载 /system", font=FONTS["body_bold"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=8, height=42,
            command=self._remount
        )
        self.remount_btn.pack(side="left")

        # 重启选项
        reboot_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        reboot_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            reboot_card, text="设备重启", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        reboot_btn_frame = ctk.CTkFrame(reboot_card, fg_color="transparent")
        reboot_btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        reboots = [
            ("正常重启", ""),
            ("重启到 Recovery", "recovery"),
            ("重启到 Bootloader", "bootloader"),
        ]
        for text, mode in reboots:
            btn = ctk.CTkButton(
                reboot_btn_frame, text=text, font=FONTS["body_bold"],
                fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                corner_radius=8, height=38,
                command=lambda m=mode: self._reboot(m)
            )
            btn.pack(side="left", padx=(0, 10))

        # 警告信息
        warn_card = ctk.CTkFrame(content, fg_color="#2A1A1A", corner_radius=12)
        warn_card.pack(fill="x")

        ctk.CTkLabel(
            warn_card, text="⚠️ 警告", font=FONTS["heading"],
            text_color=COLORS["danger"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        warnings = [
            "Root 操作可能导致设备变砖，请谨慎操作",
            "获取 Root 权限可能使设备失去保修资格",
            "请确保已备份重要数据",
            "某些操作需要设备已解锁 Bootloader",
        ]
        for w in warnings:
            ctk.CTkLabel(
                warn_card, text=f"  • {w}", font=FONTS["small"],
                text_color=COLORS["text_secondary"], anchor="w"
            ).pack(anchor="w", padx=20, pady=(0, 3))

        # 底部留白
        ctk.CTkLabel(warn_card, text="").pack(pady=3)

    def _request_root(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        self.root_btn.configure(state="disabled", text="正在获取 Root...")
        self.status_value.configure(text="正在获取 Root 权限...", text_color=COLORS["info"])

        def on_done(code, out, err):
            self.after(0, lambda: self._on_root_result(code, out, err))

        self.adb.root(on_done)

    def _on_root_result(self, code, out, err):
        self.root_btn.configure(state="normal", text="获取 Root 权限")
        if code == 0 and "restarting" in out.lower():
            self.status_value.configure(text="✅ Root 权限已获取 (设备将重启 adbd)", text_color=COLORS["success"])
            self.tip_label.configure(text="✅ Root 权限获取成功！设备 adbd 将以 root 权限重启")
        elif code == 0:
            self.status_value.configure(text="✅ 已具有 Root 权限", text_color=COLORS["success"])
            self.tip_label.configure(text="✅ 设备已具有 Root 权限")
        else:
            self.status_value.configure(text="❌ Root 获取失败", text_color=COLORS["danger"])
            self.tip_label.configure(text=f"❌ Root 失败: {err or out}")

    def _remount(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        self.remount_btn.configure(state="disabled", text="挂载中...")

        def on_done(code, out, err):
            self.after(0, lambda: self._on_remount_result(code, out, err))

        self.adb.remount(on_done)

    def _on_remount_result(self, code, out, err):
        self.remount_btn.configure(state="normal", text="重新挂载 /system")
        if code == 0:
            self.tip_label.configure(text="✅ /system 已重新挂载为可读写")
        else:
            self.tip_label.configure(text=f"❌ 挂载失败: {err or out}")

    def _reboot(self, mode):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        mode_text = {"": "正常重启", "recovery": "重启到 Recovery", "bootloader": "重启到 Bootloader"}

        self.tip_label.configure(text=f"⏳ 正在{mode_text.get(mode, mode)}...")

        def on_done(code, out, err):
            self.after(0, lambda: self._on_reboot_done(code, out, err))

        self.adb.reboot_device(mode, on_done)

    def _on_reboot_done(self, code, out, err):
        if code == 0:
            self.tip_label.configure(text="✅ 设备正在重启，请稍后重新连接")
        else:
            self.tip_label.configure(text=f"❌ 重启失败: {err}")

    def on_show(self):
        if self.adb.is_connected:
            self.tip_label.configure(text="✅ 设备已连接，可以使用 Root 工具")
        else:
            self.tip_label.configure(text="⚠️ 请先连接设备后再使用 Root 工具")