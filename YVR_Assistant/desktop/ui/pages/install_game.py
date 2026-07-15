"""
安装游戏页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QListWidget, QListWidgetItem,
    QFileDialog, QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.adb_utils import get_devices, install_apk
from desktop.ui.styles import *


class InstallWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, apk_path, serial):
        super().__init__()
        self.apk_path = apk_path
        self.serial = serial

    def run(self):
        self.progress.emit("正在安装，请稍候...")
        result = install_apk(self.apk_path, self.serial)
        if result["success"]:
            self.progress.emit("安装成功！")
            self.finished.emit(True, "安装成功")
        else:
            err = result["stderr"] or result["stdout"] or "未知错误"
            self.progress.emit(f"安装失败: {err}")
            self.finished.emit(False, err)


class InstallGamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._apk_queue = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ---------- 标题 ----------
        title = QLabel("安装游戏")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("将 APK 安装包安装到已连接的设备上")
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

        # ---------- 添加 APK 按钮 ----------
        btn_row = QHBoxLayout()
        self.btn_add_apk = QPushButton("+ 添加 APK 文件")
        self.btn_add_apk.setMinimumHeight(44)
        self.btn_add_apk.clicked.connect(self._add_apk_files)
        btn_row.addWidget(self.btn_add_apk)

        self.btn_clear = QPushButton("清空列表")
        self.btn_clear.setObjectName("btnOutline")
        self.btn_clear.clicked.connect(self._clear_queue)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()

        self.btn_install = QPushButton("开始安装")
        self.btn_install.setObjectName("btnSuccess")
        self.btn_install.setMinimumHeight(44)
        self.btn_install.setMinimumWidth(140)
        self.btn_install.clicked.connect(self._start_install)
        btn_row.addWidget(self.btn_install)
        layout.addLayout(btn_row)

        # ---------- APK 列表 ----------
        list_label = QLabel("安装队列：")
        list_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; font-weight: 600;")
        layout.addWidget(list_label)

        self.apk_list = QListWidget()
        self.apk_list.setMinimumHeight(200)
        self.apk_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 12px 14px;
                border-radius: 6px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{
                background-color: {BG_HOVER};
            }}
        """)
        layout.addWidget(self.apk_list)

        # ---------- 进度条 ----------
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximum(0)  # 不确定进度
        layout.addWidget(self.progress)

        self.progress_text = QLabel("")
        self.progress_text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.progress_text)

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

    def _add_apk_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择 APK 文件", "", "APK 文件 (*.apk);;所有文件 (*)"
        )
        for f in files:
            if f not in self._apk_queue:
                self._apk_queue.append(f)
                item = QListWidgetItem(os.path.basename(f))
                item.setToolTip(f)
                self.apk_list.addItem(item)

    def _clear_queue(self):
        self._apk_queue.clear()
        self.apk_list.clear()

    def _start_install(self):
        serial = self.device_combo.currentText()
        if not serial or serial == "无设备":
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        if not self._apk_queue:
            QMessageBox.warning(self, "提示", "请先添加 APK 文件！")
            return

        self.progress.setVisible(True)
        self.progress_text.setText("正在安装...")
        self.btn_install.setEnabled(False)

        # 逐个安装
        self._current_idx = 0
        self._install_next(serial)

    def _install_next(self, serial):
        if self._current_idx >= len(self._apk_queue):
            self.progress.setVisible(False)
            self.progress_text.setText("全部安装完成！")
            self.btn_install.setEnabled(True)
            QMessageBox.information(self, "完成", "所有 APK 安装完毕！")
            return

        apk = self._apk_queue[self._current_idx]
        self.progress_text.setText(f"正在安装 ({self._current_idx + 1}/{len(self._apk_queue)}): {os.path.basename(apk)}")

        self.worker = InstallWorker(apk, serial)
        self.worker.progress.connect(lambda msg: self.progress_text.setText(msg))
        self.worker.finished.connect(lambda success, msg: self._on_install_finished(success, msg, serial))
        self.worker.start()

    def _on_install_finished(self, success, msg, serial):
        if success:
            self._current_idx += 1
            self._install_next(serial)
        else:
            self.progress.setVisible(False)
            self.btn_install.setEnabled(True)
            self.progress_text.setText(f"安装失败: {msg}")
            QMessageBox.critical(self, "安装失败", f"安装失败:\n{msg}")