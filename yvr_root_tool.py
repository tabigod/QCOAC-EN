#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YVR Root Tool
=================
一款用于 YVR 头显 (YVR 1 / 2 / PFD MR) 的可视化 Root 工具
功能:
    1. 打开原生设置
    2. 解锁 Bootloader
    3. 解锁 Bootloader 并刷入已修补的 boot 镜像
    4. 安装 Root 管理器 + LSP
    5. 安装安卓驱动
    6. 安装 2D 启动器 + Xposed

作者: AI 生成  |  可公开使用 / 二次开发
"""

import os
import sys
import time
import threading
import subprocess
import webbrowser
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ============================================================
#  全局主题配置
# ============================================================
ctk.set_appearance_mode("dark")          # 深色模式
ctk.set_default_color_theme("blue")      # 蓝色主题

# 自定义配色
COLOR_BG       = "#0F1117"   # 主背景
COLOR_CARD     = "#1A1D29"   # 卡片背景
COLOR_ACCENT   = "#4F8CFF"   # 主题蓝
COLOR_ACCENT_H = "#3A6FD4"   # 悬停蓝
COLOR_SUCCESS  = "#2ECC71"   # 成功绿
COLOR_WARN     = "#F39C12"   # 警告橙
COLOR_DANGER   = "#E74C3C"   # 危险红
COLOR_TEXT     = "#E8EAED"   # 主文字
COLOR_SUBTEXT  = "#9AA0A6"   # 次要文字


# ============================================================
#  ADB / Fastboot 命令封装
# ============================================================
class ADBHelper:
    """ADB / Fastboot 命令执行器"""

    # 跨平台 adb / fastboot 调用
    @staticmethod
    def _run(cmd: list, log=None, realtime=True):
        """执行命令并实时输出日志, 返回 (returncode, output)"""
        if log:
            log(f"$ {' '.join(cmd)}\n", "cmd")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=ADBHelper._creation_flags(),
            )
            output_lines = []
            for line in iter(process.stdout.readline, ""):
                output_lines.append(line)
                if log and realtime:
                    log(line.rstrip("\n"), "out")
            process.wait()
            return process.returncode, "".join(output_lines)
        except FileNotFoundError:
            msg = "未找到 adb / fastboot 程序，请先安装 Android Platform-Tools 并加入 PATH。"
            if log:
                log(msg, "error")
            return -1, msg
        except Exception as e:
            msg = f"执行异常: {e}"
            if log:
                log(msg, "error")
            return -1, msg

    @staticmethod
    def _creation_flags():
        """Windows 下隐藏控制台窗口"""
        if sys.platform.startswith("win"):
            return 0x08000000  # CREATE_NO_WINDOW
        return 0

    # ---------- 设备检测 ----------
    @staticmethod
    def get_devices(log=None):
        rc, out = ADBHelper._run(["adb", "devices"], log=log, realtime=False)
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if line and "\t" in line:
                devices.append(line.split("\t")[0])
        return devices

    @staticmethod
    def get_fastboot_devices(log=None):
        rc, out = ADBHelper._run(["fastboot", "devices"], log=log, realtime=False)
        devices = []
        for line in out.splitlines():
            line = line.strip()
            if line and "\tfastboot" in line:
                devices.append(line.split("\t")[0])
        return devices

    # ---------- 命令快捷方法 ----------
    @staticmethod
    def adb_shell(shell_cmd: str, log=None):
        return ADBHelper._run(["adb", "shell", shell_cmd], log=log)

    @staticmethod
    def adb_reboot(target: str, log=None):
        return ADBHelper._run(["adb", "reboot", target], log=log)

    @staticmethod
    def fastboot(cmd_list: list, log=None):
        return ADBHelper._run(["fastboot"] + cmd_list, log=log)

    @staticmethod
    def adb_install(apk_path: str, log=None):
        return ADBHelper._run(["adb", "install", "-r", "-g", apk_path], log=log)

    @staticmethod
    def adb_push(local: str, remote: str, log=None):
        return ADBHelper._run(["adb", "push", local, remote], log=log)


# ============================================================
#  控制台日志组件
# ============================================================
class ConsoleBox(ctk.CTkTextbox):
    """带颜色标签的控制台输出"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=("Consolas", 12),
            wrap="word",
            state="disabled",
        )
        # 颜色标签
        self.tag_config("cmd",   foreground="#569CD6")
        self.tag_config("out",   foreground="#E8EAED")
        self.tag_config("info",  foreground="#4FC3F7")
        self.tag_config("ok",    foreground="#2ECC71")
        self.tag_config("warn",  foreground="#F39C12")
        self.tag_config("error", foreground="#E74C3C")
        self.tag_config("title", foreground="#BB86FC", font=("Consolas", 12, "bold"))

    def log(self, text: str, level="out"):
        self.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.insert("end", f"[{ts}] ", level)
        self.insert("end", text + "\n", level)
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


# ============================================================
#  功能按钮卡片
# ============================================================
class ActionCard(ctk.CTkFrame):
    """单个功能卡片: 图标 + 标题 + 描述 + 按钮"""

    def __init__(self, master, index, icon, title, desc, color, command, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=COLOR_CARD,
            corner_radius=14,
            border_width=1,
            border_color="#2A2E3C",
        )

        # 编号徽标
        self.badge = ctk.CTkLabel(
            self, text=str(index), width=34, height=34,
            fg_color=color, text_color="white",
            font=("Segoe UI", 15, "bold"), corner_radius=17,
        )
        self.badge.grid(row=0, column=0, padx=(18, 10), pady=(18, 0), sticky="n")

        # 图标
        self.icon_lbl = ctk.CTkLabel(
            self, text=icon, font=("Segoe UI Emoji", 26),
            text_color=color,
        )
        self.icon_lbl.grid(row=0, column=1, padx=(0, 12), pady=(18, 0), sticky="n")

        # 标题
        self.title_lbl = ctk.CTkLabel(
            self, text=title, anchor="w",
            font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT,
        )
        self.title_lbl.grid(row=0, column=2, padx=0, pady=(20, 0), sticky="w")

        # 描述
        self.desc_lbl = ctk.CTkLabel(
            self, text=desc, anchor="w", justify="left",
            font=("Segoe UI", 11), text_color=COLOR_SUBTEXT,
        )
        self.desc_lbl.grid(row=1, column=1, columnspan=2, padx=(0, 18),
                           pady=(4, 14), sticky="ew")

        # 执行按钮
        self.btn = ctk.CTkButton(
            self, text="执 行", width=80, height=32,
            font=("Segoe UI", 12, "bold"),
            fg_color=color, hover_color=COLOR_ACCENT_H,
            command=command, corner_radius=8,
        )
        self.btn.grid(row=0, column=3, padx=(12, 18), pady=(18, 0), sticky="n")

        self.grid_columnconfigure(2, weight=1)


# ============================================================
#  主应用窗口
# ============================================================
class YVRRootToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------- 窗口基础 ----------
        self.title("YVR Root Tool  ·  玩出梦想头显 Root 工具箱")
        self.geometry("960x760")
        self.minsize(880, 700)
        self.configure(fg_color=COLOR_BG)

        # ---------- 顶部标题栏 ----------
        self._build_header()

        # ---------- 设备状态栏 ----------
        self._build_status_bar()

        # ---------- 功能卡片网格 ----------
        self._build_action_grid()

        # ---------- 控制台 ----------
        self._build_console()

        # ---------- 底部状态 ----------
        self._build_footer()

        # 启动时自动检测设备
        self.after(500, self.refresh_device_status)

    # ==================== UI 构建 ====================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG, height=90)
        header.pack(fill="x", padx=24, pady=(18, 0))
        header.pack_propagate(False)

        # LOGO 圆
        logo = ctk.CTkLabel(
            header, text="🎮", font=("Segoe UI Emoji", 34),
            width=64, height=64, fg_color=COLOR_ACCENT,
            corner_radius=32, text_color="white",
        )
        logo.pack(side="left", padx=(4, 16))

        title_box = ctk.CTkFrame(header, fg_color=COLOR_BG)
        title_box.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_box, text="YVR Root Tool",
            font=("Segoe UI", 22, "bold"), text_color=COLOR_TEXT,
        ).pack(anchor="w", pady=(14, 0))
        ctk.CTkLabel(
            title_box, text="玩出梦想 YVR 1 / 2 / PFD MR  ·  一键 Root 工具箱",
            font=("Segoe UI", 12), text_color=COLOR_SUBTEXT,
        ).pack(anchor="w")

        # 右上角刷新按钮
        self.refresh_btn = ctk.CTkButton(
            header, text="🔄 刷新设备", width=110, height=34,
            font=("Segoe UI", 12), fg_color=COLOR_CARD,
            hover_color="#252938", text_color=COLOR_TEXT,
            border_width=1, border_color="#2A2E3C",
            command=self.refresh_device_status,
        )
        self.refresh_btn.pack(side="right", padx=4)

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=12,
                           height=48, border_width=1, border_color="#2A2E3C")
        bar.pack(fill="x", padx=24, pady=(14, 0))
        bar.pack_propagate(False)

        self.status_dot = ctk.CTkLabel(bar, text="●", font=("Segoe UI", 16),
                                       text_color=COLOR_WARN)
        self.status_dot.pack(side="left", padx=(18, 6))

        self.status_text = ctk.CTkLabel(
            bar, text="正在检测设备...",
            font=("Segoe UI", 13), text_color=COLOR_TEXT, anchor="w",
        )
        self.status_text.pack(side="left", padx=(0, 18))

        self.device_count_lbl = ctk.CTkLabel(
            bar, text="", font=("Segoe UI", 12), text_color=COLOR_SUBTEXT,
        )
        self.device_count_lbl.pack(side="right", padx=18)

    def _build_action_grid(self):
        grid = ctk.CTkFrame(self, fg_color=COLOR_BG)
        grid.pack(fill="both", expand=True, padx=24, pady=(14, 0))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        actions = [
            (1, "⚙️", "打开原生设置",
             "进入 Android 系统原生 Settings 界面\n用于调试 WiFi 开发者选项等",
             COLOR_ACCENT, self.action_open_settings),
            (2, "🔓", "解锁 Bootloader",
             "重启进入 Bootloader 并执行解锁\n⚠️ 将清除设备全部数据",
             COLOR_WARN, self.action_unlock_bl),
            (3, "📦", "解锁并刷入修补 boot",
             "解锁 BL 后刷入已修补的 boot.img\n配合 Magisk/APatch 实现 Root",
             COLOR_DANGER, self.action_unlock_and_flash_boot),
            (4, "🛡️", "安装 Root 管理器 + LSP",
             "安装 Magisk/APatch 管理器及 LSPosed\n提供模块化 Hook 框架",
             COLOR_SUCCESS, self.action_install_root_lsp),
            (5, "🔌", "安装安卓驱动",
             "安装 ADB / Fastboot USB 驱动\n保证设备能被电脑正确识别",
             "#9B59B6", self.action_install_driver),
            (6, "🖥️", "安装 2D 启动器 + Xposed",
             "安装 2D Launcher 及 Xposed 框架\n让头显可运行 2D 安卓应用",
             "#1ABC9C", self.action_install_2d_launcher),
        ]

        for i, (idx, icon, title, desc, color, cmd) in enumerate(actions):
            row, col = divmod(i, 2)
            card = ActionCard(grid, idx, icon, title, desc, color, cmd)
            card.grid(row=row, column=col, padx=(0 if col == 0 else 7, 7 if col == 0 else 0),
                      pady=(0, 12), sticky="nsew")

    def _build_console(self):
        console_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=12,
                                     border_width=1, border_color="#2A2E3C")
        console_frame.pack(fill="x", padx=24, pady=(14, 0))

        # 控制台标题行
        top = ctk.CTkFrame(console_frame, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(top, text="🖥️  控制台输出",
                     font=("Segoe UI", 13, "bold"),
                     text_color=COLOR_TEXT).pack(side="left")
        ctk.CTkButton(top, text="清空", width=60, height=26,
                      font=("Segoe UI", 11), fg_color="transparent",
                      hover_color="#252938", text_color=COLOR_SUBTEXT,
                      border_width=1, border_color="#2A2E3C",
                      command=self.clear_console).pack(side="right")

        self.console = ConsoleBox(console_frame, height=180,
                                  fg_color="#0A0C12", corner_radius=8,
                                  border_width=1, border_color="#1F2330")
        self.console.pack(fill="x", padx=14, pady=(0, 12))

        # 欢迎信息
        self.console.log("=" * 56, "title")
        self.console.log("  YVR Root Tool 已就绪  ·  请选择上方功能执行", "info")
        self.console.log("  支持: YVR 1 / YVR 2 / PFD MR  及其它安卓头显", "info")
        self.console.log("=" * 56, "title")

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=COLOR_BG, height=30)
        footer.pack(fill="x", padx=24, pady=(8, 14))
        ctk.CTkLabel(
            footer, text="⚠️ 解锁 Bootloader 将清除全部数据，请提前备份；本工具仅供学习研究使用",
            font=("Segoe UI", 10), text_color=COLOR_SUBTEXT,
        ).pack(side="left")
        ctk.CTkLabel(
            footer, text="Made with ❤️  ·  AI Generated",
            font=("Segoe UI", 10), text_color=COLOR_SUBTEXT,
        ).pack(side="right")

    # ==================== 设备状态 ====================
    def refresh_device_status(self):
        """后台检测设备状态"""
        def worker():
            self.refresh_btn.configure(state="disabled", text="检测中...")
            adb_devices = ADBHelper.get_devices()
            fb_devices = ADBHelper.get_fastboot_devices()
            self.refresh_btn.configure(state="normal", text="🔄 刷新设备")

            if adb_devices:
                self.status_dot.configure(text_color=COLOR_SUCCESS)
                self.status_text.configure(
                    text=f"设备已连接 (ADB 模式): {adb_devices[0]}")
                self.device_count_lbl.configure(
                    text=f"ADB: {len(adb_devices)}  |  Fastboot: {len(fb_devices)}")
                self.console.log(f"✅ 检测到 ADB 设备: {adb_devices}", "ok")
            elif fb_devices:
                self.status_dot.configure(text_color=COLOR_WARN)
                self.status_text.configure(
                    text=f"设备已连接 (Fastboot 模式): {fb_devices[0]}")
                self.device_count_lbl.configure(
                    text=f"Fastboot: {len(fb_devices)}")
                self.console.log(f"⚠️ 设备处于 Fastboot 模式: {fb_devices}", "warn")
            else:
                self.status_dot.configure(text_color=COLOR_DANGER)
                self.status_text.configure(text="未检测到设备，请连接设备并开启 USB 调试")
                self.device_count_lbl.configure(text="")
                self.console.log("❌ 未检测到任何设备", "error")

        threading.Thread(target=worker, daemon=True).start()

    # ==================== 通用方法 ====================
    def clear_console(self):
        self.console.clear()

    def run_in_thread(self, func):
        """在后台线程执行，避免阻塞 UI"""
        threading.Thread(target=func, daemon=True).start()

    def check_adb_device(self):
        devices = ADBHelper.get_devices()
        if not devices:
            self.console.log("❌ 未检测到 ADB 设备，请先连接并开启 USB 调试", "error")
            messagebox.showerror("设备未连接",
                                 "未检测到 ADB 设备。\n请:\n1. 用 USB 连接头显与电脑\n"
                                 "2. 在头显设置中开启 开发者选项 → USB 调试\n"
                                 "3. 在头显弹窗中点击 允许调试")
            return False
        return True

    def check_fastboot_device(self):
        devices = ADBHelper.get_fastboot_devices()
        if not devices:
            self.console.log("❌ 未检测到 Fastboot 设备", "error")
            return False
        return True

    def select_file(self, title, filetypes):
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        return path

    def confirm(self, title, msg):
        return messagebox.askyesno(title, msg)

    # ==================== 功能实现 ====================
    # 1. 打开原生设置
    def action_open_settings(self):
        def task():
            self.console.log("\n▶ [1] 打开原生设置", "title")
            if not self.check_adb_device():
                return
            self.console.log("正在启动 Android Settings...", "info")
            # 多种 settings 启动方式兼容
            cmds = [
                "am start -n com.android.settings/.Settings",
                "am start -a android.settings.SETTINGS",
                "am start -n com.android.settings/.Settings\\$AllSettingsActivity",
            ]
            for c in cmds:
                rc, _ = ADBHelper.adb_shell(c, log=self.console.log)
                if rc == 0:
                    self.console.log("✅ 原生设置已打开，请在头显端查看", "ok")
                    return
            self.console.log("⚠️ 所有启动方式均失败，设备可能未包含原生设置应用", "warn")

        self.run_in_thread(task)

    # 2. 解锁 Bootloader
    def action_unlock_bl(self):
        if not self.confirm(
            "⚠️ 解锁 Bootloader 确认",
            "解锁 Bootloader 将:\n"
            "  • 清除设备全部用户数据\n"
            "  • 可能使保修失效\n"
            "  • 解锁后设备将处于不安全状态\n\n"
            "请确认已备份重要数据，是否继续？"):
            return

        def task():
            self.console.log("\n▶ [2] 解锁 Bootloader", "title")
            if not self.check_adb_device():
                return
            self.console.log("步骤 1/3: 重启进入 Bootloader 模式...", "info")
            ADBHelper.adb_reboot("bootloader", log=self.console.log)
            self.console.log("等待设备进入 Fastboot 模式 (8秒)...", "info")
            time.sleep(8)

            if not self.check_fastboot_device():
                self.console.log("请在头显端确认是否允许解锁，然后重试", "warn")
                return

            self.console.log("步骤 2/3: 执行 flashing unlock...", "info")
            rc, _ = ADBHelper.fastboot(["flashing", "unlock"],
                                       log=self.console.log)
            self.console.log("请查看头显屏幕，使用音量键选择 UNLOCK THE BOOTLOADER 并按电源键确认",
                             "warn")
            self.console.log("等待用户在设备端确认 (15秒)...", "info")
            time.sleep(15)

            self.console.log("步骤 3/3: 重启设备...", "info")
            ADBHelper.fastboot(["reboot"], log=self.console.log)
            self.console.log("✅ Bootloader 解锁流程已完成", "ok")

        self.run_in_thread(task)

    # 3. 解锁 BL 并刷入已修补 boot
    def action_unlock_and_flash_boot(self):
        boot_img = self.select_file(
            "选择已修补的 boot.img",
            [("Boot 镜像", "*.img"), ("所有文件", "*.*")])
        if not boot_img:
            self.console.log("已取消选择 boot 镜像", "warn")
            return

        if not self.confirm(
            "⚠️ 刷入 boot 镜像确认",
            f"将执行:\n  1. 解锁 Bootloader (清除数据)\n"
            f"  2. 刷入已修补的 boot 镜像:\n     {os.path.basename(boot_img)}\n\n"
            f"⚠️ 刷入错误的 boot 可能导致设备无法启动!\n是否继续？"):
            return

        def task():
            self.console.log("\n▶ [3] 解锁 BL + 刷入修补 boot", "title")
            if not self.check_adb_device():
                return

            # --- 解锁 ---
            self.console.log("阶段 A: 解锁 Bootloader", "info")
            ADBHelper.adb_reboot("bootloader", log=self.console.log)
            self.console.log("等待进入 Fastboot (8秒)...", "info")
            time.sleep(8)
            if not self.check_fastboot_device():
                return
            ADBHelper.fastboot(["flashing", "unlock"], log=self.console.log)
            self.console.log("请在设备端确认解锁 (15秒)...", "warn")
            time.sleep(15)

            # --- 刷入 boot ---
            self.console.log("阶段 B: 刷入已修补 boot 镜像", "info")
            self.console.log(f"刷入文件: {boot_img}", "info")
            rc, _ = ADBHelper.fastboot(["flash", "boot", boot_img],
                                       log=self.console.log)
            if rc != 0:
                self.console.log("❌ 刷入 boot 失败，请检查镜像是否匹配当前设备",
                                 "error")
                ADBHelper.fastboot(["reboot"], log=self.console.log)
                return
            self.console.log("✅ boot 镜像刷入成功，正在重启...", "ok")
            ADBHelper.fastboot(["reboot"], log=self.console.log)
            self.console.log("✅ 全部完成！重启后即获得 Root 权限", "ok")

        self.run_in_thread(task)

    # 4. 安装 Root 管理器 + LSP
    def action_install_root_lsp(self):
        magisk_apk = self.select_file(
            "选择 Magisk / APatch 管理器 APK",
            [("APK 文件", "*.apk"), ("所有文件", "*.*")])
        if not magisk_apk:
            self.console.log("已取消选择 Root 管理器 APK", "warn")
            return

        lsp_apk = self.select_file(
            "选择 LSPosed 模块 APK / ZIP (可跳过)",
            [("APK/ZIP", "*.apk *.zip"), ("所有文件", "*.*")])

        def task():
            self.console.log("\n▶ [4] 安装 Root 管理器 + LSP", "title")
            if not self.check_adb_device():
                return

            self.console.log("阶段 A: 安装 Root 管理器 APK", "info")
            rc, _ = ADBHelper.adb_install(magisk_apk, log=self.console.log)
            if rc == 0:
                self.console.log("✅ Root 管理器安装成功", "ok")
            else:
                self.console.log("❌ Root 管理器安装失败", "error")
                return

            if lsp_apk:
                self.console.log("阶段 B: 安装 LSPosed", "info")
                if lsp_apk.lower().endswith(".zip"):
                    # LSPosed 模块通常以 zip 形式通过 Magisk 安装
                    remote = "/data/local/tmp/lsposed.zip"
                    ADBHelper.adb_push(lsp_apk, remote, log=self.console.log)
                    ADBHelper.adb_shell(
                        f"su -c 'magisk --install-module {remote}'",
                        log=self.console.log)
                    self.console.log("✅ LSPosed 模块已推送，请在 Magisk 中确认安装并重启",
                                     "ok")
                else:
                    rc, _ = ADBHelper.adb_install(lsp_apk, log=self.console.log)
                    if rc == 0:
                        self.console.log("✅ LSPosed APK 安装成功", "ok")
                    else:
                        self.console.log("⚠️ LSPosed 安装失败，可手动安装", "warn")
            else:
                self.console.log("已跳过 LSPosed 安装", "info")

            self.console.log("提示: 请在头显中打开 Root 管理器完成后续配置", "info")

        self.run_in_thread(task)

    # 5. 安装安卓驱动
    def action_install_driver(self):
        def task():
            self.console.log("\n▶ [5] 安装安卓驱动", "title")
            if sys.platform.startswith("win"):
                self.console.log("检测到 Windows 系统，正在引导安装 ADB USB 驱动...",
                                 "info")
                self.console.log("提示: 推荐使用 Google USB Driver 或厂商通用驱动", "info")
                urls = [
                    ("Google USB Driver 下载页",
                     "https://developer.android.com/studio/run/win-usb"),
                    ("15 seconds ADB Installer (一键安装)",
                     "https://forum.xda-developers.com/t/official-tool-15-seconds-adb-installer-v1-4-3.2542724/"),
                ]
                self.console.log("即将打开驱动下载网页，请在浏览器中下载并安装:", "info")
                for name, url in urls:
                    self.console.log(f"  - {name}: {url}", "out")
                # 打开官方下载页
                webbrowser.open(urls[0][1])
                self.console.log("✅ 已打开浏览器，请下载并安装驱动后重新连接设备", "ok")
            elif sys.platform.startswith("linux"):
                self.console.log("Linux 系统通常无需额外驱动，请确认 udev 规则已配置", "info")
                self.console.log("提示: 可执行 sudo apt install android-tools-adb fastboot",
                                 "out")
                self.console.log("如需 udev 规则: "
                                 "sudo nano /etc/udev/rules.d/51-android.rules", "out")
            else:
                self.console.log("macOS 系统通常无需额外驱动，请安装 android-platform-tools",
                                 "info")
                self.console.log("提示: brew install android-platform-tools", "out")

        self.run_in_thread(task)

    # 6. 安装 2D 启动器 + Xposed
    def action_install_2d_launcher(self):
        launcher_apk = self.select_file(
            "选择 2D 启动器 APK (如: 第三方桌面 / 2D Launcher)",
            [("APK 文件", "*.apk"), ("所有文件", "*.*")])
        if not launcher_apk:
            self.console.log("已取消选择 2D 启动器 APK", "warn")
            return

        xp_apk = self.select_file(
            "选择 Xposed 框架 APK / ZIP (如 LSPosed / EdXposed, 可跳过)",
            [("APK/ZIP", "*.apk *.zip"), ("所有文件", "*.*")])

        def task():
            self.console.log("\n▶ [6] 安装 2D 启动器 + Xposed", "title")
            if not self.check_adb_device():
                return

            self.console.log("阶段 A: 安装 2D 启动器", "info")
            rc, _ = ADBHelper.adb_install(launcher_apk, log=self.console.log)
            if rc == 0:
                self.console.log("✅ 2D 启动器安装成功", "ok")
                # 设为默认桌面 (可选)
                self.console.log("尝试设为默认桌面...", "info")
                ADBHelper.adb_shell(
                    "cmd package set-home-activity "
                    "$(pm resolve-activity --brief -c android.intent.category.HOME "
                    "| tail -1)", log=self.console.log)
            else:
                self.console.log("⚠️ 2D 启动器安装失败", "warn")

            if xp_apk:
                self.console.log("阶段 B: 安装 Xposed 框架", "info")
                if xp_apk.lower().endswith(".zip"):
                    remote = "/data/local/tmp/xposed.zip"
                    ADBHelper.adb_push(xp_apk, remote, log=self.console.log)
                    ADBHelper.adb_shell(
                        f"su -c 'magisk --install-module {remote}'",
                        log=self.console.log)
                    self.console.log("✅ Xposed 模块已推送，请在 Magisk 中确认并重启", "ok")
                else:
                    rc, _ = ADBHelper.adb_install(xp_apk, log=self.console.log)
                    if rc == 0:
                        self.console.log("✅ Xposed APK 安装成功", "ok")
                    else:
                        self.console.log("⚠️ Xposed 安装失败", "warn")
            else:
                self.console.log("已跳过 Xposed 安装", "info")

            self.console.log("提示: 重启头显后在 2D 启动器中即可运行 2D 安卓应用", "info")

        self.run_in_thread(task)


# ============================================================
#  入口
# ============================================================
def check_adb_available():
    """启动前检测 adb 是否可用 (仅提示，不阻断)"""
    try:
        subprocess.run(["adb", "version"],
                       capture_output=True, creationflags=0x08000000
                       if sys.platform.startswith("win") else 0)
        return True
    except FileNotFoundError:
        return False


def main():
    if not check_adb_available():
        print("⚠️  警告: 未检测到 adb 命令，部分功能将不可用。")
        print("    请安装 Android Platform-Tools 并将其加入 PATH:")
        print("    https://developer.android.com/studio/releases/platform-tools")
        print()

    app = YVRRootToolApp()
    app.mainloop()


if __name__ == "__main__":
    main()
