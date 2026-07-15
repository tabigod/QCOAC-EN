"""
ADB 命令页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
import sys
import os
import shlex

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.adb_utils import get_devices, run_adb_command
from desktop.ui.styles import *


class ADBCommandsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._command_history = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ---------- 标题 ----------
        title = QLabel("ADB 命令")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("直接执行 ADB 命令，完全控制设备")
        subtitle.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        # ---------- 设备选择 ----------
        sel_row = QHBoxLayout()
        sel_label = QLabel("目标设备：")
        sel_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        sel_row.addWidget(sel_label)

        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(280)
        sel_row.addWidget(self.device_combo)

        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.setObjectName("btnOutline")
        self.btn_refresh.clicked.connect(self._refresh_devices)
        sel_row.addWidget(self.btn_refresh)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # ---------- 设备状态 ----------
        self.status_label = QLabel("未连接设备")
        self.status_label.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; "
            f"padding: 10px 16px; font-size: 13px; color: {WARNING};"
        )
        layout.addWidget(self.status_label)

        # ---------- 快捷命令 ----------
        quick_label = QLabel("快捷命令：")
        quick_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; font-weight: 600;")
        layout.addWidget(quick_label)

        quick_row1 = QHBoxLayout()
        for cmd, label_text in [
            ("devices", "设备列表"),
            ("shell wm size", "屏幕分辨率"),
            ("shell getprop ro.build.version.release", "Android 版本"),
            ("shell dumpsys battery", "电池信息"),
        ]:
            btn = QPushButton(label_text)
            btn.setObjectName("btnOutline")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1.5px solid {BORDER};
                    color: {TEXT_SECONDARY};
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    border-color: {PRIMARY};
                    color: {PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, c=cmd: self._set_quick_command(c))
            quick_row1.addWidget(btn)
        quick_row1.addStretch()
        layout.addLayout(quick_row1)

        quick_row2 = QHBoxLayout()
        for cmd, label_text in [
            ("shell pm list packages", "已安装应用"),
            ("shell cat /proc/cpuinfo", "CPU 信息"),
            ("shell cat /proc/meminfo", "内存信息"),
            ("shell df -h", "磁盘空间"),
        ]:
            btn = QPushButton(label_text)
            btn.setObjectName("btnOutline")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1.5px solid {BORDER};
                    color: {TEXT_SECONDARY};
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    border-color: {PRIMARY};
                    color: {PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, c=cmd: self._set_quick_command(c))
            quick_row2.addWidget(btn)
        quick_row2.addStretch()
        layout.addLayout(quick_row2)

        # ---------- 命令输入 ----------
        cmd_label = QLabel("ADB 命令：")
        cmd_label.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 600;")
        layout.addWidget(cmd_label)

        cmd_row = QHBoxLayout()
        self.cmd_prefix = QLabel("adb")
        self.cmd_prefix.setStyleSheet(
            f"background-color: {BG_INPUT}; border: 1.5px solid {BORDER}; border-radius: 8px 0 0 8px; "
            f"padding: 10px 14px; color: {ACCENT}; font-weight: bold; font-size: 13px;"
        )
        cmd_row.addWidget(self.cmd_prefix)

        self.cmd_input = QTextEdit()
        self.cmd_input.setMaximumHeight(60)
        self.cmd_input.setPlaceholderText("输入 ADB 命令参数（如 devices, shell ls /sdcard）...")
        self.cmd_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_INPUT};
                border: 1.5px solid {BORDER};
                border-left: none;
                border-radius: 0 8px 8px 0;
                padding: 10px 14px;
                color: {TEXT_PRIMARY};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 13px;
            }}
        """)
        cmd_row.addWidget(self.cmd_input)

        self.btn_exec = QPushButton("执行")
        self.btn_exec.setObjectName("btnSuccess")
        self.btn_exec.setMinimumHeight(60)
        self.btn_exec.clicked.connect(self._exec_command)
        cmd_row.addWidget(self.btn_exec)
        layout.addLayout(cmd_row)

        # ---------- 输出 ----------
        output_label = QLabel("命令输出：")
        output_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; font-weight: 600;")
        layout.addWidget(output_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_INPUT};
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.output_text)

        layout.addStretch()

        self._refresh_devices()

    def _refresh_devices(self):
        self.device_combo.clear()
        devices = get_devices()
        if devices:
            self.device_combo.addItems(devices)
            self.status_label.setText(f"已连接 {len(devices)} 台设备")
            self.status_label.setStyleSheet(
                f"background-color: {BG_CARD}; border: 1px solid {SUCCESS}; border-radius: 8px; "
                f"padding: 10px 16px; font-size: 13px; color: {SUCCESS};"
            )
        else:
            self.device_combo.addItem("无设备")
            self.status_label.setText("未连接设备 - 请先连接设备")
            self.status_label.setStyleSheet(
                f"background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; "
                f"padding: 10px 16px; font-size: 13px; color: {WARNING};"
            )

    def _get_serial(self):
        s = self.device_combo.currentText()
        return s if s and s != "无设备" else None

    def _set_quick_command(self, cmd):
        self.cmd_input.setPlainText(cmd)

    def _exec_command(self):
        cmd_text = self.cmd_input.toPlainText().strip()
        if not cmd_text:
            return

        serial = self._get_serial()
        if serial and "devices" not in cmd_text and "shell" in cmd_text:
            # 自动添加 -s 参数
            result = run_adb_command(["-s", serial] + shlex.split(cmd_text))
        else:
            result = run_adb_command(shlex.split(cmd_text))

        output = result["stdout"] if result["success"] else f"错误:\n{result['stderr']}"
        self.output_text.setPlainText(output)
        self._command_history.append(cmd_text)