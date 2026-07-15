"""
YVR助手 - ADB 管理核心模块
负责 ADB 路径检测、设备连接、命令执行
"""

import os
import sys
import subprocess
import threading
from pathlib import Path


def get_adb_path():
    """获取 ADB 可执行文件路径，优先使用打包附带的 ADB"""
    base_dir = Path(__file__).resolve().parent.parent

    # 打包后的路径
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent

    # 优先使用项目自带的 adb
    adb_dir = base_dir / "adb"
    adb_exe = adb_dir / "adb.exe"
    if adb_exe.exists():
        return str(adb_exe)

    # 检查系统环境变量中的 adb
    import shutil
    system_adb = shutil.which("adb")
    if system_adb:
        return system_adb

    return "adb"


class ADBManager:
    """ADB 操作管理器（单例模式）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._adb_path = get_adb_path()
        self._connected = False
        self._device_serial = None
        self._device_model = None
        self._callback = None

    @property
    def adb_path(self):
        return self._adb_path

    @property
    def is_connected(self):
        return self._connected

    @property
    def device_serial(self):
        return self._device_serial

    @property
    def device_model(self):
        return self._device_model

    def set_status_callback(self, callback):
        """设置连接状态变化回调"""
        self._callback = callback

    def _notify(self):
        if self._callback:
            self._callback(self._connected, self._device_model)

    def _run(self, cmd, timeout=15):
        """执行 ADB 命令"""
        full_cmd = f'"{self._adb_path}" {cmd}'
        try:
            result = subprocess.run(
                full_cmd, shell=True, capture_output=True, text=True,
                timeout=timeout, encoding='utf-8', errors='replace'
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "命令执行超时"
        except Exception as e:
            return -1, "", str(e)

    def _run_async(self, cmd, callback, timeout=30):
        """异步执行 ADB 命令"""
        def _target():
            code, out, err = self._run(cmd, timeout)
            if callback:
                callback(code, out, err)
        t = threading.Thread(target=_target, daemon=True)
        t.start()
        return t

    def check_adb(self):
        """检查 ADB 是否可用"""
        code, out, _ = self._run("version")
        return code == 0

    def refresh_connection(self):
        """刷新设备连接状态"""
        code, out, _ = self._run("devices")
        if code != 0:
            self._connected = False
            self._device_serial = None
            self._device_model = None
            self._notify()
            return False, "ADB 不可用"

        lines = out.strip().split('\n')[1:]  # 跳过第一行 "List of devices"
        devices = [l.split('\t')[0] for l in lines if '\tdevice' in l]

        if devices:
            self._connected = True
            self._device_serial = devices[0]
            # 获取设备型号
            _, model_out, _ = self._run(f"-s {self._device_serial} shell getprop ro.product.model")
            self._device_model = model_out.strip() if model_out.strip() else "未知设备"
            self._notify()
            return True, self._device_model
        else:
            self._connected = False
            self._device_serial = None
            self._device_model = None
            self._notify()
            return False, "未检测到已连接的设备"

    def get_device_info(self):
        """获取设备详细信息"""
        if not self._connected:
            return None

        info = {}
        props = {
            "ro.product.model": "设备型号",
            "ro.product.brand": "品牌",
            "ro.product.manufacturer": "制造商",
            "ro.build.version.release": "Android 版本",
            "ro.build.version.sdk": "SDK 版本",
            "ro.build.display.id": "Build ID",
            "ro.product.cpu.abi": "CPU 架构",
            "ro.hardware": "硬件平台",
        }

        for prop, label in props.items():
            code, out, _ = self._run(f"-s {self._device_serial} shell getprop {prop}")
            info[label] = out.strip() if code == 0 else "未知"

        # 获取屏幕分辨率
        code, out, _ = self._run(f"-s {self._device_serial} shell wm size")
        info["屏幕分辨率"] = out.strip().split(":")[-1].strip() if code == 0 and ":" in out else "未知"

        # 获取电池信息
        code, out, _ = self._run(f"-s {self._device_serial} shell dumpsys battery")
        if code == 0:
            for line in out.split('\n'):
                line = line.strip()
                if line.startswith("level:"):
                    info["电量"] = line.split(":")[1].strip() + "%"
                elif line.startswith("temperature:"):
                    temp = int(line.split(":")[1].strip()) / 10
                    info["温度"] = f"{temp}°C"

        return info

    def install_apk(self, apk_path, callback=None):
        """安装 APK"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} install -r "{apk_path}"'
        self._run_async(cmd, callback, timeout=120)

    def uninstall_app(self, package_name, callback=None):
        """卸载应用"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} uninstall {package_name}'
        self._run_async(cmd, callback, timeout=30)

    def list_packages(self, callback=None):
        """列出已安装的应用包名"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} shell pm list packages'
        self._run_async(cmd, callback, timeout=30)

    def list_files(self, remote_path="/sdcard/", callback=None):
        """列出设备文件"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} shell ls -la "{remote_path}"'
        self._run_async(cmd, callback, timeout=15)

    def push_file(self, local_path, remote_path, callback=None):
        """推送文件到设备"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} push "{local_path}" "{remote_path}"'
        self._run_async(cmd, callback, timeout=60)

    def pull_file(self, remote_path, local_path, callback=None):
        """从设备拉取文件"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} pull "{remote_path}" "{local_path}"'
        self._run_async(cmd, callback, timeout=60)

    def delete_file(self, remote_path, callback=None):
        """删除设备文件"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} shell rm -rf "{remote_path}"'
        self._run_async(cmd, callback, timeout=15)

    def mkdir(self, remote_path, callback=None):
        """创建远程目录"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} shell mkdir -p "{remote_path}"'
        self._run_async(cmd, callback, timeout=10)

    def reboot_device(self, mode="", callback=None):
        """重启设备"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        mode_cmd = f" {mode}" if mode else ""
        cmd = f'-s {self._device_serial} reboot{mode_cmd}'
        self._run_async(cmd, callback, timeout=10)

    def screencap(self, local_path, callback=None):
        """截取设备屏幕"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        remote_tmp = "/sdcard/yvr_screencap_tmp.png"
        cmd = f'-s {self._device_serial} shell screencap -p {remote_tmp} && '
        cmd += f'"{self._adb_path}" -s {self._device_serial} pull {remote_tmp} "{local_path}" && '
        cmd += f'"{self._adb_path}" -s {self._device_serial} shell rm {remote_tmp}'
        self._run_async(cmd, callback, timeout=15)

    def raw_command(self, cmd, callback=None, timeout=30):
        """执行原始 ADB 命令"""
        self._run_async(cmd, callback, timeout=timeout)

    def root(self, callback=None):
        """尝试获取 Root 权限"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} root'
        self._run_async(cmd, callback, timeout=10)

    def remount(self, callback=None):
        """重新挂载系统分区为可读写"""
        if not self._connected:
            if callback:
                callback(-1, "", "设备未连接")
            return
        cmd = f'-s {self._device_serial} remount'
        self._run_async(cmd, callback, timeout=10)