"""
设备信息页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QComboBox, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))))
from shared.adb_utils import get_devices, get_device_info
from desktop.ui.styles import *


class DeviceInfoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ---------- 标题 ----------
        title = QLabel("设备信息")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("查看已连接设备的详细信息")
        subtitle.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        # ---------- 设备选择行 ----------
        sel_row = QHBoxLayout()
        sel_label = QLabel("选择设备：")
        sel_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        sel_row.addWidget(sel_label)

        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(280)
        self.device_combo.setStyleSheet(
            f"QComboBox {{ background-color: {BG_INPUT}; border: 1.5px solid {BORDER}; border-radius: 8px; padding: 10px 14px; color: {TEXT_PRIMARY}; font-size: 13px; }}"
            f"QComboBox:hover {{ border-color: {PRIMARY}; }}"
        )
        sel_row.addWidget(self.device_combo)

        self.btn_refresh_devices = QPushButton("刷新设备")
        self.btn_refresh_devices.setObjectName("btnOutline")
        self.btn_refresh_devices.clicked.connect(self._refresh_devices)
        sel_row.addWidget(self.btn_refresh_devices)

        self.btn_get_info = QPushButton("获取信息")
        self.btn_get_info.clicked.connect(self._load_device_info)
        sel_row.addWidget(self.btn_get_info)

        sel_row.addStretch()
        layout.addLayout(sel_row)

        # ---------- 设备状态指示 ----------
        self.status_label = QLabel("未连接设备")
        self.status_label.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; "
            f"padding: 10px 16px; font-size: 13px; color: {WARNING};"
        )
        layout.addWidget(self.status_label)

        # ---------- 信息卡片区域 ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")

        info_widget = QWidget()
        self.info_layout = QVBoxLayout(info_widget)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(16)

        # 基本信息卡片
        self.basic_group = self._create_info_group("基本信息", [])
        self.info_layout.addWidget(self.basic_group)

        # 系统信息卡片
        self.system_group = self._create_info_group("系统信息", [])
        self.info_layout.addWidget(self.system_group)

        # 硬件信息卡片
        self.hardware_group = self._create_info_group("硬件信息", [])
        self.info_layout.addWidget(self.hardware_group)

        self.info_layout.addStretch()
        scroll.setWidget(info_widget)
        layout.addWidget(scroll)

        # 初始加载设备
        QTimer.singleShot(200, self._refresh_devices)

    def _create_info_group(self, title, items):
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                margin-top: 16px;
                padding: 20px 20px 16px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 18px;
                padding: 0 10px;
                color: {PRIMARY};
            }}
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        return group

    def _add_info_row(self, group, label, value):
        row = QHBoxLayout()
        row.setSpacing(12)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; min-width: 100px;")
        lbl.setFixedWidth(120)
        row.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row.addWidget(val)
        row.addStretch()
        group.layout().addLayout(row)

    def _clear_group(self, group):
        """清空 group 中的旧内容"""
        lay = group.layout()
        while lay.count():
            item = lay.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()
        # 确保 layout 干净
        QTimer.singleShot(0, lambda: self._really_clear(lay))

    def _really_clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()

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
            self.status_label.setText("未连接设备 - 请通过 USB 或 WiFi 连接设备")
            self.status_label.setStyleSheet(
                f"background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; "
                f"padding: 10px 16px; font-size: 13px; color: {WARNING};"
            )

    def _load_device_info(self):
        serial = self.device_combo.currentText()
        if not serial or serial == "无设备":
            return

        self.status_label.setText("正在获取设备信息...")
        self.status_label.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {ACCENT}; border-radius: 8px; "
            f"padding: 10px 16px; font-size: 13px; color: {ACCENT};"
        )

        info = get_device_info(serial)

        # 清空并重新填充
        self._clear_group(self.basic_group)
        self._add_info_row(self.basic_group, "设备型号", info.get("model", "未知"))
        self._add_info_row(self.basic_group, "设备品牌", info.get("brand", "未知"))
        self._add_info_row(self.basic_group, "序列号", info.get("serial", "未知"))

        self._clear_group(self.system_group)
        self._add_info_row(self.system_group, "Android 版本", info.get("android_version", "未知"))
        self._add_info_row(self.system_group, "SDK 版本", info.get("sdk_version", "未知"))
        self._add_info_row(self.system_group, "分辨率", info.get("resolution", "未知"))
        self._add_info_row(self.system_group, "电池电量", info.get("battery", "未知"))

        self._clear_group(self.hardware_group)
        self._add_info_row(self.hardware_group, "CPU 架构", info.get("cpu_abi", "未知"))

        self.status_label.setText("设备信息获取完成")
        self.status_label.setStyleSheet(
            f"background-color: {BG_CARD}; border: 1px solid {SUCCESS}; border-radius: 8px; "
            f"padding: 10px 16px; font-size: 13px; color: {SUCCESS};"
        )