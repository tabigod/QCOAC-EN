"""
YVR助手 - Web 端 Flask 应用
提供 REST API 供前端调用
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from shared.adb_utils import (
    get_devices, get_device_info, install_apk,
    list_files, push_file, pull_file, delete_file,
    get_root_status, run_adb_command, screen_capture,
    execute_shell
)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return render_template('index.html')


# ========== 设备相关 ==========

@app.route('/api/devices', methods=['GET'])
def api_devices():
    devices = get_devices()
    return jsonify({"success": True, "devices": devices})


@app.route('/api/device/info', methods=['POST'])
def api_device_info():
    data = request.get_json()
    serial = data.get("serial", "")
    info = get_device_info(serial)
    return jsonify({"success": True, "info": info})


# ========== 安装游戏 ==========

@app.route('/api/install', methods=['POST'])
def api_install():
    data = request.get_json()
    serial = data.get("serial", "")
    apk_path = data.get("apk_path", "")
    if not apk_path or not os.path.exists(apk_path):
        return jsonify({"success": False, "error": "APK 文件不存在"})
    result = install_apk(apk_path, serial)
    return jsonify(result)


# ========== 文件管理 ==========

@app.route('/api/files', methods=['POST'])
def api_files():
    data = request.get_json()
    serial = data.get("serial", "")
    path = data.get("path", "/sdcard/")
    files = list_files(path, serial)
    return jsonify({"success": True, "files": files, "path": path})


@app.route('/api/file/push', methods=['POST'])
def api_file_push():
    data = request.get_json()
    serial = data.get("serial", "")
    local = data.get("local", "")
    remote = data.get("remote", "")
    result = push_file(local, remote, serial)
    return jsonify(result)


@app.route('/api/file/pull', methods=['POST'])
def api_file_pull():
    data = request.get_json()
    serial = data.get("serial", "")
    remote = data.get("remote", "")
    local = data.get("local", "")
    result = pull_file(remote, local, serial)
    return jsonify(result)


@app.route('/api/file/delete', methods=['POST'])
def api_file_delete():
    data = request.get_json()
    serial = data.get("serial", "")
    path = data.get("path", "")
    result = delete_file(path, serial)
    return jsonify(result)


# ========== Root ==========

@app.route('/api/root/status', methods=['POST'])
def api_root_status():
    data = request.get_json()
    serial = data.get("serial", "")
    status = get_root_status(serial)
    return jsonify({"success": True, "status": status})


@app.route('/api/root/enable', methods=['POST'])
def api_root_enable():
    data = request.get_json()
    serial = data.get("serial", "")
    result = run_adb_command(["-s", serial, "root"])
    return jsonify(result)


@app.route('/api/shell', methods=['POST'])
def api_shell():
    data = request.get_json()
    serial = data.get("serial", "")
    cmd = data.get("cmd", "")
    result = execute_shell(cmd, serial)
    return jsonify(result)


# ========== VR 投屏 ==========

@app.route('/api/screenshot', methods=['POST'])
def api_screenshot():
    data = request.get_json()
    serial = data.get("serial", "")
    save_path = data.get("save_path", "")
    result = screen_capture(serial, save_path)
    return jsonify(result)


# ========== ADB 命令 ==========

@app.route('/api/adb', methods=['POST'])
def api_adb():
    data = request.get_json()
    serial = data.get("serial", "")
    cmd = data.get("cmd", "")
    import shlex
    args = shlex.split(cmd)
    if serial and "devices" not in cmd:
        args = ["-s", serial] + args
    result = run_adb_command(args)
    return jsonify(result)


if __name__ == '__main__':
    print("=" * 50)
    print("  YVR助手 Web 版")
    print("  请在浏览器中打开: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)