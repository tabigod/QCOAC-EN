"""
YVR助手 - 设备信息页面
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS


class DeviceInfoPage(ctk.CTkFrame):
    """设备信息页面 - 显示已连接设备的详细信息"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="设备信息", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            header, text="刷新信息", font=FONTS["body_bold"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=8, width=100, height=34,
            command=self.refresh
        )
        self.refresh_btn.pack(side="right")

        ctk.CTkLabel(
            header, text="查看已连接设备的详细信息",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="right", padx=(0, 15))

        # 提示区域
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再查看设备信息",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=15)

        # 信息卡片容器
        self.info_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border_light"],
            scrollbar_button_hover_color=COLORS["text_muted"],
        )
        self.info_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.cards = {}
        self._create_info_cards()

    def _create_info_cards(self):
        """创建信息卡片"""
        sections = [
            ("基本", ["设备型号", "品牌", "制造商"]),
            ("系统", ["Android 版本", "SDK 版本", "Build ID"]),
            ("硬件", ["CPU 架构", "硬件平台", "屏幕分辨率"]),
            ("状态", ["电量", "温度"]),
        ]

        for section_name, fields in sections:
            card = self._create_card(section_name, fields)
            card.pack(fill="x", pady=(0, 12))
            self.cards[section_name] = card

    def _create_card(self, title, fields):
        card = ctk.CTkFrame(self.info_container, fg_color=COLORS["bg_card"], corner_radius=12)

        ctk.CTkLabel(
            card, text=title, font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 15))

        # 网格布局：每行两个字段
        for i, field in enumerate(fields):
            row = i // 2
            col = i % 2

            field_frame = ctk.CTkFrame(content, fg_color=COLORS["bg_input"], corner_radius=8)
            field_frame.grid(row=row, column=col, padx=(0 if col == 0 else 5, 5 if col == 0 else 0), pady=4, sticky="ew")

            ctk.CTkLabel(
                field_frame, text=field, font=FONTS["small"],
                text_color=COLORS["text_muted"]
            ).pack(anchor="w", padx=12, pady=(8, 0))

            value_label = ctk.CTkLabel(
                field_frame, text="--", font=FONTS["body_bold"],
                text_color=COLORS["text_primary"]
            )
            value_label.pack(anchor="w", padx=12, pady=(0, 8))

            # 存储引用以便更新
            setattr(card, f"val_{field}", value_label)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        return card

    def refresh(self):
        """刷新设备信息"""
        self.refresh_btn.configure(state="disabled", text="刷新中...")
        self.after(100, self._do_refresh)

    def _do_refresh(self):
        connected, _ = self.adb.refresh_connection()

        if not connected:
            self.tip_label.configure(text="⚠️ 请先连接设备后再查看设备信息")
            self._clear_info()
        else:
            info = self.adb.get_device_info()
            if info:
                self.tip_label.configure(text="✅ 设备信息已更新")
                self._update_info(info)
            else:
                self.tip_label.configure(text="⚠️ 无法获取设备信息")
                self._clear_info()

        self.refresh_btn.configure(state="normal", text="刷新信息")

    def _update_info(self, info):
        """更新信息卡片"""
        field_to_label = {
            "设备型号": "val_设备型号", "品牌": "val_品牌", "制造商": "val_制造商",
            "Android 版本": "val_Android 版本", "SDK 版本": "val_SDK 版本",
            "Build ID": "val_Build ID", "CPU 架构": "val_CPU 架构",
            "硬件平台": "val_硬件平台", "屏幕分辨率": "val_屏幕分辨率",
            "电量": "val_电量", "温度": "val_温度",
        }

        for section_name, card in self.cards.items():
            for field, attr in field_to_label.items():
                if hasattr(card, attr):
                    value = info.get(field, "--")
                    label = getattr(card, attr)
                    label.configure(text=value)

    def _clear_info(self):
        """清空信息"""
        for card in self.cards.values():
            for attr in dir(card):
                if attr.startswith("val_"):
                    getattr(card, attr).configure(text="--")

    def on_show(self):
        """页面显示时调用"""
        self.refresh()