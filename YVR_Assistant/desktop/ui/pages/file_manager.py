"""
文件管理页面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QInputDialog, QLineEdit, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.adb_utils import (
    get_devices, list_files, push_file, pull_file,
    delete_file, execute_shell
)
from desktop.ui.styles import *


class FileManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path = "/sdcard/"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ---------- 标题 ----------
        title = QLabel("文件管理")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("浏览和管理设备上的文件")
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

        # ---------- 路径导航 ----------
        nav_row = QHBoxLayout()
        self.btn_back = QPushButton("← 上级目录")
        self.btn_back.setObjectName("btnOutline")
        self.btn_back.clicked.connect(self._go_up)
        nav_row.addWidget(self.btn_back)

        self.path_display = QLineEdit(self._current_path)
        self.path_display.setReadOnly(True)
        self.path_display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                color: {ACCENT};
                font-size: 13px;
            }}
        """)
        nav_row.addWidget(self.path_display)

        self.btn_go = QPushButton("跳转")
        self.btn_go.clicked.connect(self._jump_to_path)
        nav_row.addWidget(self.btn_go)
        layout.addLayout(nav_row)

        # ---------- 操作按钮 ----------
        op_row = QHBoxLayout()
        self.btn_upload = QPushButton("上传文件到设备")
        self.btn_upload.clicked.connect(self._upload_file)
        op_row.addWidget(self.btn_upload)

        self.btn_download = QPushButton("下载选中文件")
        self.btn_download.clicked.connect(self._download_file)
        op_row.addWidget(self.btn_download)

        self.btn_delete = QPushButton("删除选中")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self._delete_file)
        op_row.addWidget(self.btn_delete)

        self.btn_new_folder = QPushButton("新建文件夹")
        self.btn_new_folder.setObjectName("btnOutline")
        self.btn_new_folder.clicked.connect(self._new_folder)
        op_row.addWidget(self.btn_new_folder)
        op_row.addStretch()
        layout.addLayout(op_row)

        # ---------- 文件列表 ----------
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(300)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.file_list)

        # ---------- 进度条 ----------
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

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
            self._load_files()
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

    def _load_files(self):
        serial = self._get_serial()
        if not serial:
            return
        self.file_list.clear()
        self.path_display.setText(self._current_path)
        files = list_files(self._current_path, serial)
        for f in files:
            item = QListWidgetItem(f)
            self.file_list.addItem(item)

    def _go_up(self):
        if self._current_path == "/":
            return
        self._current_path = os.path.dirname(self._current_path.rstrip("/"))
        if not self._current_path:
            self._current_path = "/"
        if not self._current_path.endswith("/"):
            self._current_path += "/"
        self._load_files()

    def _jump_to_path(self):
        serial = self._get_serial()
        if not serial:
            return
        path, ok = QInputDialog.getText(self, "跳转路径", "输入设备路径:", text=self._current_path)
        if ok and path:
            self._current_path = path if path.endswith("/") else path + "/"
            self._load_files()

    def _on_item_double_clicked(self, item):
        text = item.text().strip()
        # 解析 ls -la 输出，提取文件名
        parts = text.split()
        if len(parts) >= 9:
            name = " ".join(parts[8:])
        elif len(parts) >= 1:
            name = parts[-1]
        else:
            return

        if text.startswith("d"):
            # 目录
            self._current_path = os.path.join(self._current_path, name).replace("\\", "/")
            if not self._current_path.endswith("/"):
                self._current_path += "/"
            self._load_files()

    def _get_selected_filename(self):
        item = self.file_list.currentItem()
        if not item:
            return None
        parts = item.text().strip().split()
        if len(parts) >= 9:
            return " ".join(parts[8:])
        return parts[-1] if parts else None

    def _get_selected_full_path(self):
        name = self._get_selected_filename()
        if not name:
            return None
        return (self._current_path.rstrip("/") + "/" + name)

    def _upload_file(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        local, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if not local:
            return
        remote = self._current_path + os.path.basename(local)
        self.progress.setVisible(True)
        result = push_file(local, remote, serial)
        self.progress.setVisible(False)
        if result["success"]:
            QMessageBox.information(self, "完成", "文件上传成功！")
            self._load_files()
        else:
            QMessageBox.critical(self, "失败", f"上传失败:\n{result['stderr']}")

    def _download_file(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        name = self._get_selected_filename()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择要下载的文件！")
            return
        remote = self._get_selected_full_path()
        save_dir = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if not save_dir:
            return
        local = os.path.join(save_dir, name)
        self.progress.setVisible(True)
        result = pull_file(remote, local, serial)
        self.progress.setVisible(False)
        if result["success"]:
            QMessageBox.information(self, "完成", f"文件已保存到:\n{local}")
        else:
            QMessageBox.critical(self, "失败", f"下载失败:\n{result['stderr']}")

    def _delete_file(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        name = self._get_selected_filename()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择要删除的文件！")
            return
        remote = self._get_selected_full_path()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 \"{name}\" 吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        result = delete_file(remote, serial)
        if result["success"]:
            QMessageBox.information(self, "完成", "删除成功！")
            self._load_files()
        else:
            QMessageBox.critical(self, "失败", f"删除失败:\n{result['stderr']}")

    def _new_folder(self):
        serial = self._get_serial()
        if not serial:
            QMessageBox.warning(self, "提示", "请先连接设备！")
            return
        name, ok = QInputDialog.getText(self, "新建文件夹", "输入文件夹名称:")
        if ok and name:
            path = self._current_path.rstrip("/") + "/" + name
            execute_shell(f"mkdir -p {path}", serial)
            self._load_files()