"""
Root 管理页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.adb_utils import get_devices, get_root_status, execute_shell, run_adb_command
from desktop.ui.styles import *


class RootPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ---------- 标题 ----------
        title = QLabel("Root 管理")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("检查和管理设备的 Root 权限状态")
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

        # ---------- Root 状态 ----------
        self.status_label = QLabel("未连接设备")
        self.status_label.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; "
            f"padding: 10px 16px; font-size: 13px; color: {WARNING};"
        )
        layout.addWidget(self.status_label)

        # ---------- Root 状态卡片 ----------
        self.root_status_frame = QFrame()
        self.root_status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        root_layout = QVBoxLayout(self.root_status_frame)
        root_layout.setSpacing(14)

        self.root_icon_label = QLabel("🔒")
        self.root_icon_label.setStyleSheet(f"font-size: 48px; background: transparent;")
        self.root_icon_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(self.root_icon_label)

        self.root_status_text = QLabel("请先连接设备并检查 Root 状态")
        self.root_status_text.setStyleSheet(f"font-size: 15px; color: {TEXT_SECONDARY}; background: transparent;")
        self.root_status_text.setAlignment(Qt.AlignCenter)
        self.root_status_text.setWordWrap(True)
        root_layout.addWidget(self.root_status_text)

        layout.addWidget(self.root_status_frame)

        # ---------- 操作按钮 ----------
        btn_row = QHBoxLayout()
        self.btn_check = QPushButton("检查 Root 状态")
        self.btn_check.clicked.connect(self._check_root)
        btn_row.addWidget(self.btn_check)

        self.btn_enable_root = QPushButton("启用 ADB Root")
        self.btn_enable_root.clicked.connect(self._enable_root)
        btn_row.addWidget(self.btn_enable_root)

        self.btn_reboot = QPushButton("重启设备")
        self.btn_reboot.setObjectName("btnOutline")
        self.btn_reboot.clicked.connect(self._reboot_device)
        btn_row.addWidget(self.btn_reboot)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ---------- Shell 命令 ----------
        shell_label = QLabel("执行 Shell 命令：")
        shell_label.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 600; margin-top: 10px;")
        layout.addWidget(shell_label)

        cmd_row = QHBoxLayout()
        self.shell_input = QTextEdit()
        self.shell_input.setMaximumHeight(80)
        self.shell_input.setPlaceholderText("输入 ADB shell 命令...")
        cmd_row.addWidget(self.shell_input)

        self.btn_exec = QPushButton("执行")
        self.btn_exec.setObjectName("btnSuccess")
        self.btn_exec.clicked.connect(self._exec_shell)
        cmd_row.addWidget(self.btn_exec)
        layout.addLayout(cmd_row)

        # ---------- 输出 ----------
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
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

        # 初始加载
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

    def _check_root(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        status = get_root_status(serial)
        if status["rooted"]:
            self.root_icon_label.setText("✅")
            self.root_status_text.setText(f"设备已 Root\n{status['detail']}")
            self.root_status_text.setStyleSheet(
                f"font-size: 15px; color: {SUCCESS}; background: transparent;"
            )
        else:
            self.root_icon_label.setText("🔒")
            self.root_status_text.setText(f"设备未 Root\n{status['detail']}")
            self.root_status_text.setStyleSheet(
                f"font-size: 15px; color: {WARNING}; background: transparent;"
            )

    def _enable_root(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        result = run_adb_command(["-s", serial, "root"])
        if result["success"]:
            QMessageBox.information(self, "完成", "ADB Root 已启用！")
            self._check_root()
        else:
            QMessageBox.critical(self, "失败", f"启用 Root 失败:\n{result['stderr']}")

    def _reboot_device(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        reply = QMessageBox.question(
            self, "确认重启", "确定要重启设备吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            run_adb_command(["-s", serial, "reboot"])
            QMessageBox.information(self, "提示", "设备正在重启...")

    def _exec_shell(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        cmd = self.shell_input.toPlainText().strip()
        if not cmd:
            return
        result = execute_shell(cmd, serial)
        output = result["stdout"] if result["success"] else result["stderr"]
        self.output_text.setPlainText(output)