"""
YVR助手 - ADB 命令页面
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS


class ADBCommandPage(ctk.CTkFrame):
    """ADB 命令页面 - 自定义 ADB 命令执行"""

    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self._command_history = []
        self._build()

    def _build(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header, text="ADB 命令", font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="执行自定义 ADB 命令",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(15, 0))

        # 提示
        self.tip_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.tip_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.tip_label = ctk.CTkLabel(
            self.tip_frame,
            text="⚠️ 请先连接设备后再执行 ADB 命令",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        )
        self.tip_label.pack(pady=15)

        # 内容区域
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # 命令输入区域
        input_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        input_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            input_card, text="输入命令", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 快捷命令
        quick_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            quick_frame, text="快捷命令:", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 8))

        quick_commands = [
            ("查看设备", "devices"),
            ("包列表", "shell pm list packages"),
            ("当前Activity", "shell dumpsys window | grep mCurrentFocus"),
            ("屏幕信息", "shell wm size"),
            ("内存信息", "shell dumpsys meminfo"),
            ("CPU信息", "shell cat /proc/cpuinfo"),
        ]

        for label, cmd in quick_commands:
            btn = ctk.CTkButton(
                quick_frame, text=label, font=FONTS["small"],
                fg_color=COLORS["bg_input"], hover_color=COLORS["accent"],
                corner_radius=6, height=26,
                command=lambda c=cmd: self._set_command(c)
            )
            btn.pack(side="left", padx=(0, 5))

        # 命令行输入
        cmd_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        cmd_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.cmd_entry = ctk.CTkEntry(
            cmd_frame, font=FONTS["mono"], height=38,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=8, placeholder_text="输入 ADB 命令..."
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", lambda e: self._execute_command())

        self.exec_btn = ctk.CTkButton(
            cmd_frame, text="▶ 执行", font=FONTS["body_bold"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
            corner_radius=8, width=80, height=38,
            command=self._execute_command
        )
        self.exec_btn.pack(side="right")

        # 输出区域
        output_card = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        output_card.pack(fill="both", expand=True)

        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            output_header, text="命令输出", font=FONTS["heading"],
            text_color=COLORS["accent_light"]
        ).pack(side="left")

        self.clear_output_btn = ctk.CTkButton(
            output_header, text="清空输出", font=FONTS["small"],
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
            corner_radius=6, height=26, width=70,
            command=self._clear_output
        )
        self.clear_output_btn.pack(side="right")

        self.output_text = ctk.CTkTextbox(
            output_card, font=("Consolas", 11),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=8, text_color=COLORS["text_primary"],
            border_width=1
        )
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.output_text.insert("1.0", "等待 ADB 命令执行...\n\n")
        self.output_text.configure(state="disabled")

    def _set_command(self, cmd):
        self.cmd_entry.delete(0, "end")
        self.cmd_entry.insert(0, cmd)
        self.cmd_entry.focus()

    def _execute_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return

        self.exec_btn.configure(state="disabled", text="执行中...")

        self._append_output(f"\n>>> adb {cmd}\n", COLORS["accent_light"])
        self._command_history.append(cmd)

        def on_done(code, out, err):
            self.after(0, lambda: self._on_command_done(code, out, err))

        self.adb.raw_command(cmd, on_done)

    def _on_command_done(self, code, out, err):
        self.exec_btn.configure(state="normal", text="▶ 执行")

        if out:
            self._append_output(out + "\n", COLORS["text_primary"])
        if err:
            self._append_output(err + "\n", COLORS["danger"])

        if code == 0:
            self._append_output(f"[返回码: {code} - 成功]\n", COLORS["success"])
        else:
            self._append_output(f"[返回码: {code} - 失败]\n", COLORS["warning"])

    def _append_output(self, text, color=None):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text)
        if color:
            # 为最后插入的文本添加颜色标签
            start = self.output_text.index("end-2l")
            end = self.output_text.index("end-1c")
            tag = f"color_{hash(color)}"
            self.output_text.tag_config(tag, foreground=color)
            self.output_text.tag_add(tag, start, end)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def _clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", "输出已清空\n\n")
        self.output_text.configure(state="disabled")

    def on_show(self):
        if self.adb.is_connected:
            self.tip_label.configure(text="✅ 设备已连接，可以执行 ADB 命令")
        else:
            self.tip_label.configure(text="⚠️ 请先连接设备后再执行 ADB 命令")