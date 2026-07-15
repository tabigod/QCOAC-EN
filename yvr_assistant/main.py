"""
YVR助手 - 主入口文件
一款美观实用的 Windows VR 设备管理工具
"""

import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import YVRAssistant


def main():
    app = YVRAssistant()
    app.mainloop()


if __name__ == "__main__":
    main()