"""
YVR助手 - VR 投屏页面
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import COLORS, FONTS


class VRScreenPage(ctk.CTkFrame):
    """VR 投屏页面 - 屏幕截图与录制"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._screenshot_dir = os.path.expanduser("~/Pictures/YVR_Screenshots")
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="VR 投屏", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="屏幕截图与实时投屏",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 0))

        # 提示
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再使用投屏功能",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=15)

        # 内容区域
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # 截图区域
        capture_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        capture_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            capture_card, text="屏幕截图", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        cap_inner = ctk.CTkFrame(capture_card, fg_color="transparent")
        cap_inner.pack(fill="x", padx=20, pady=(0, 15))

        self.capture_btn = ctk.CTkButton(
            cap_inner, text="📸 截取当前屏幕", font=FONTS["body_bold"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=8, height=42, width=180,
            command=self._capture_screen
        )
        self.capture_btn.pack(side="left", padx=(0, 15))

        self.capture_status = ctk.CTkLabel(
            cap_inner, text="点击按钮截取设备屏幕",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.capture_status.pack(side="left")

        # 保存路径设置
        path_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        path_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            path_card, text="保存路径", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        path_inner = ctk.CTkFrame(path_card, fg_color="transparent")
        path_inner.pack(fill="x", padx=20, pady=(0, 15))

        self.path_label = ctk.CTkLabel(
            path_inner, text=self._screenshot_dir, font=FONTS["mono"],
            text_color=COLORS["text_primary"]
        )
        self.path_label.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            path_inner, text="更改路径", font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, height=30, width=80,
            command=self._change_path
        ).pack(side="left")

        ctk.CTkButton(
            path_inner, text="打开文件夹", font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, height=30, width=90,
            command=self._open_folder
        ).pack(side="left", padx=(8, 0))

        # 投屏预览区域
        preview_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        preview_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            preview_card, text="实时预览", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        preview_inner = ctk.CTkFrame(
            preview_card, fg_color=COLORS["bg_input"], corner_radius=8,
            border_width=2, border_color=COLORS["border"]
        )
        preview_inner.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.preview_label = ctk.CTkLabel(
            preview_inner, text="设备屏幕预览将显示在此处\n\n请先连接设备并点击截图",
            font=FONTS["body"], text_color=COLORS["text_muted"],
            width=400, height=250
        )
        self.preview_label.pack(expand=True)

        self.preview_img = None

    def _capture_screen(self):
        if not self.adb.is_connected:
            self.tip_label.configure(text="⚠️ 请先连接设备！")
            return

        os.makedirs(self._screenshot_dir, exist_ok=True)

        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"yvr_screenshot_{timestamp}.png"
        filepath = os.path.join(self._screenshot_dir, filename)

        self.capture_btn.configure(state="disabled", text="截图中...")
        self.capture_status.configure(text="正在截取屏幕...")

        def on_done(code, out, err):
            self.after(0, lambda: self._on_capture_done(code, out, err, filepath))

        self.adb.screencap(filepath, on_done)

    def _on_capture_done(self, code, out, err, filepath):
        self.capture_btn.configure(state="normal", text="📸 截取当前屏幕")
        if code == 0:
            self.capture_status.configure(text=f"✅ 截图已保存: {os.path.basename(filepath)}")
            self.tip_label.configure(text=f"✅ 截图成功！保存在 {filepath}")

            # 尝试显示预览
            try:
                from PIL import Image
                img = Image.open(filepath)
                img.thumbnail((380, 240))

                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.preview_label.configure(image=ctk_img, text="")
                self.preview_img = ctk_img
            except Exception:
                self.preview_label.configure(text="✅ 截图成功！\n(无法预览)")
        else:
            self.capture_status.configure(text="❌ 截图失败")
            self.tip_label.configure(text=f"❌ 截图失败: {err}")

    def _change_path(self):
        new_path = filedialog.askdirectory(title="选择截图保存目录")
        if new_path:
            self._screenshot_dir = new_path
            self.path_label.configure(text=new_path)
            os.makedirs(new_path, exist_ok=True)

    def _open_folder(self):
        os.makedirs(self._screenshot_dir, exist_ok=True)
        os.startfile(self._screenshot_dir)

    def on_show(self):
        if self.adb.is_connected:
            self.tip_label.configure(text="✅ 设备已连接，可以使用投屏功能")
        else:
            self.tip_label.configure(text="⚠️ 请先连接设备后再使用投屏功能")