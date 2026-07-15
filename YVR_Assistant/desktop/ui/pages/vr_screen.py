"""
VR 投屏页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QFrame,
    QSpinBox, QFileDialog, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.adb_utils import (
    get_devices, screen_capture, screen_record, pull_file
)
from desktop.ui.styles import *


class ScreenRecordWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str, str)

    def __init__(self, serial, duration, remote_path):
        super().__init__()
        self.serial = serial
        self.duration = duration
        self.remote_path = remote_path

    def run(self):
        self.progress.emit(f"正在录制 ({self.duration}秒)...")
        result = screen_record(self.serial, self.remote_path, self.duration)
        if result["success"]:
            self.progress.emit("录制完成！")
            self.finished.emit(True, "录制完成", self.remote_path)
        else:
            self.finished.emit(False, result.get("stderr", "录制失败"), "")


class VRScreenPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ---------- 标题 ----------
        title = QLabel("VR 投屏")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("截屏、录屏并管理设备的屏幕内容")
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

        # ---------- 截屏 ----------
        screenshot_frame = self._create_card("截屏", "截取设备当前屏幕并保存到本地")
        sc_layout = screenshot_frame.layout()

        self.btn_screenshot = QPushButton("截取屏幕")
        self.btn_screenshot.clicked.connect(self._take_screenshot)
        sc_layout.addWidget(self.btn_screenshot)

        layout.addWidget(screenshot_frame)

        # ---------- 录屏 ----------
        record_frame = self._create_card("录屏", "录制设备屏幕为视频文件")
        rc_layout = record_frame.layout()

        dur_row = QHBoxLayout()
        dur_label = QLabel("录制时长（秒）：")
        dur_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        dur_row.addWidget(dur_label)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 600)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {BG_INPUT};
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
        """)
        dur_row.addWidget(self.duration_spin)
        dur_row.addStretch()
        rc_layout.addLayout(dur_row)

        self.btn_record = QPushButton("开始录制")
        self.btn_record.clicked.connect(self._start_record)
        rc_layout.addWidget(self.btn_record)

        layout.addWidget(record_frame)

        # ---------- 进度条 ----------
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.progress_text = QLabel("")
        self.progress_text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.progress_text)

        layout.addStretch()

        self._refresh_devices()

    def _create_card(self, title, desc):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        card_layout = QVBoxLayout(frame)
        card_layout.setSpacing(12)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        card_layout.addWidget(t)

        d = QLabel(desc)
        d.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;")
        d.setWordWrap(True)
        card_layout.addWidget(d)

        return frame

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

    def _take_screenshot(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存截图", "yvr_screenshot.png", "PNG 图片 (*.png)"
        )
        if not save_path:
            return

        self.progress.setVisible(True)
        self.progress_text.setText("正在截屏...")
        result = screen_capture(serial, save_path)
        self.progress.setVisible(False)

        if result["success"]:
            self.progress_text.setText(f"截图已保存到: {save_path}")
            QMessageBox.information(self, "完成", f"截图已保存到:\n{save_path}")
        else:
            self.progress_text.setText("截屏失败")
            QMessageBox.critical(self, "失败", f"截屏失败:\n{result['stderr']}")

    def _start_record(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存录屏", "yvr_screenrecord.mp4", "MP4 视频 (*.mp4)"
        )
        if not save_path:
            return

        duration = self.duration_spin.value()
        remote_path = "/sdcard/yvr_screenrecord.mp4"

        self.progress.setVisible(True)
        self.progress.setMaximum(0)
        self.btn_record.setEnabled(False)

        self.worker = ScreenRecordWorker(serial, duration, remote_path)
        self.worker.progress.connect(lambda msg: self.progress_text.setText(msg))
        self.worker.finished.connect(lambda success, msg, rp: self._on_record_finished(success, msg, rp, save_path))
        self.worker.start()

    def _on_record_finished(self, success, msg, remote_path, save_path):
        self.progress.setVisible(False)
        self.btn_record.setEnabled(True)

        if success:
            self.progress_text.setText("正在下载录屏文件...")
            self.progress.setVisible(True)
            result = pull_file(remote_path, save_path, self._get_serial())
            self.progress.setVisible(False)
            if result["success"]:
                self.progress_text.setText(f"录屏已保存到: {save_path}")
                QMessageBox.information(self, "完成", f"录屏已保存到:\n{save_path}")
            else:
                self.progress_text.setText("下载失败")
                QMessageBox.critical(self, "失败", f"下载失败:\n{result['stderr']}")
        else:
            self.progress_text.setText(f"录制失败: {msg}")
            QMessageBox.critical(self, "失败", f"录制失败:\n{msg}")