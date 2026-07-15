"""
YVR助手 - 桌面端入口
"""
import sys
import os

# 确保能找到项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from desktop.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YVR助手")
    app.setOrganizationName("YVR")

    # 设置默认字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()