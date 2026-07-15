"""
YVR助手 - ADB 工具模块
共享的 ADB 操作工具，桌面端和 Web 端共用
"""

import os
import sys
import subprocess
import threading

# ADB 路径：优先使用附带的 ADB，否则使用系统 PATH
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ADB_DIR = os.path.join(_BASE_DIR, "adb")
_ADB_EXE = os.path.join(_ADB_DIR, "adb.exe") if sys.platform == "win32" else os.path.join(_ADB_DIR, "adb")


def get_adb_path():
    """获取 ADB 可执行文件路径"""
    if os.path.exists(_ADB_EXE):
        return _ADB_EXE
    # 回退到系统 PATH
    return "adb"


def run_adb_command(args, timeout=30):
    """执行 ADB 命令并返回结果"""
    adb = get_adb_path()
    cmd = [adb] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "命令执行超时", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": "未找到 ADB，请确保 ADB 已安装", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def get_devices():
    """获取已连接的设备列表"""
    result = run_adb_command(["devices"])
    if not result["success"]:
        return []
    devices = []
    lines = result["stdout"].split("\n")[1:]  # 跳过第一行 "List of devices attached"
    for line in lines:
        line = line.strip()
        if line and "\tdevice" in line:
            serial = line.split("\t")[0]
            devices.append(serial)
    return devices


def get_device_info(serial=None):
    """获取设备信息"""
    base = ["-s", serial] if serial else []

    info = {}

    # 设备型号
    r = run_adb_command(base + ["shell", "getprop", "ro.product.model"])
    info["model"] = r["stdout"] if r["success"] else "未知"

    # 设备品牌
    r = run_adb_command(base + ["shell", "getprop", "ro.product.brand"])
    info["brand"] = r["stdout"] if r["success"] else "未知"

    # Android 版本
    r = run_adb_command(base + ["shell", "getprop", "ro.build.version.release"])
    info["android_version"] = r["stdout"] if r["success"] else "未知"

    # SDK 版本
    r = run_adb_command(base + ["shell", "getprop", "ro.build.version.sdk"])
    info["sdk_version"] = r["stdout"] if r["success"] else "未知"

    # 设备序列号
    r = run_adb_command(base + ["shell", "getprop", "ro.serialno"])
    info["serial"] = r["stdout"] if r["success"] else (serial or "未知")

    # 分辨率
    r = run_adb_command(base + ["shell", "wm", "size"])
    if r["success"]:
        info["resolution"] = r["stdout"].replace("Physical size:", "").strip() if "Physical size:" in r["stdout"] else r["stdout"]
    else:
        info["resolution"] = "未知"

    # 电池信息
    r = run_adb_command(base + ["shell", "dumpsys", "battery"])
    if r["success"]:
        for line in r["stdout"].split("\n"):
            line = line.strip()
            if line.startswith("level:"):
                info["battery"] = line.split(":")[1].strip() + "%"

    # CPU 架构
    r = run_adb_command(base + ["shell", "getprop", "ro.product.cpu.abi"])
    info["cpu_abi"] = r["stdout"] if r["success"] else "未知"

    return info


def install_apk(apk_path, serial=None, progress_callback=None):
    """安装 APK 到设备"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["install", "-r", apk_path], timeout=120)
    if progress_callback:
        progress_callback(result)
    return result


def list_files(device_path="/sdcard/", serial=None):
    """列出设备上的文件"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["shell", "ls", "-la", device_path])
    if not result["success"]:
        return []
    files = []
    lines = result["stdout"].split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("total"):
            files.append(line)
    return files


def push_file(local_path, remote_path, serial=None):
    """推送文件到设备"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["push", local_path, remote_path], timeout=60)
    return result


def pull_file(remote_path, local_path, serial=None):
    """从设备拉取文件"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["pull", remote_path, local_path], timeout=60)
    return result


def delete_file(remote_path, serial=None):
    """删除设备上的文件"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["shell", "rm", "-rf", remote_path])
    return result


def reboot_device(serial=None, mode=""):
    """重启设备"""
    base = ["-s", serial] if serial else []
    args = ["reboot"]
    if mode in ("bootloader", "recovery", "fastboot"):
        args.append(mode)
    return run_adb_command(base + args)


def screen_capture(serial=None, save_path=None):
    """截取设备屏幕"""
    base = ["-s", serial] if serial else []
    remote_path = "/sdcard/yvr_screenshot.png"
    result = run_adb_command(base + ["shell", "screencap", "-p", remote_path])
    if not result["success"]:
        return result
    if save_path:
        result = run_adb_command(base + ["pull", remote_path, save_path])
    return result


def screen_record(serial=None, remote_path="/sdcard/yvr_screenrecord.mp4", duration=30):
    """录制设备屏幕"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["shell", "screenrecord", "--time-limit", str(duration), remote_path], timeout=duration + 10)
    return result


def execute_shell(cmd, serial=None):
    """执行 shell 命令"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["shell"] + cmd.split(), timeout=30)
    return result


def get_root_status(serial=None):
    """检查 Root 状态"""
    base = ["-s", serial] if serial else []
    result = run_adb_command(base + ["shell", "su", "-c", "id"])
    if result["success"] and "uid=0" in result["stdout"]:
        return {"rooted": True, "detail": "设备已获得 Root 权限"}
    result2 = run_adb_command(base + ["root"])
    if result2["success"]:
        return {"rooted": True, "detail": "ADB Root 已启用"}
    return {"rooted": False, "detail": "设备未 Root 或未授予 Root 权限"}