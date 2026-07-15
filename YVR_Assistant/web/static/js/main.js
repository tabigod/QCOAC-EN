/**
 * YVR助手 - Web 端前端逻辑
 */
const API_BASE = '';

// ========== 工具函数 ==========

function showToast(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showLoading(id) {
    document.getElementById(id).classList.add('active');
}

function hideLoading(id) {
    document.getElementById(id).classList.remove('active');
}

async function apiPost(url, data = {}) {
    try {
        const res = await fetch(API_BASE + url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    } catch (e) {
        return { success: false, error: '网络请求失败' };
    }
}

async function apiGet(url) {
    try {
        const res = await fetch(API_BASE + url);
        return await res.json();
    } catch (e) {
        return { success: false, error: '网络请求失败' };
    }
}

function getSelectedDevice() {
    const sel = document.getElementById('device-select');
    if (!sel) return null;
    return sel.value;
}

async function refreshDevices(selectId) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    const res = await apiGet('/api/devices');
    sel.innerHTML = '';
    if (res.devices && res.devices.length > 0) {
        res.devices.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d;
            opt.textContent = d;
            sel.appendChild(opt);
        });
        updateStatusBar(selectId, true);
    } else {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '无设备';
        sel.appendChild(opt);
        updateStatusBar(selectId, false);
    }
}

function updateStatusBar(selectId, connected) {
    // 找到同页面的 status-bar
    const page = document.getElementById(selectId)?.closest('.page');
    if (!page) return;
    const bar = page.querySelector('.status-bar');
    if (!bar) return;
    if (connected) {
        bar.textContent = '已连接设备';
        bar.className = 'status-bar success';
    } else {
        bar.textContent = '未连接设备 - 请先通过 USB 或 WiFi 连接设备';
        bar.className = 'status-bar';
    }
}

// ========== 导航 ==========

function switchPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const page = document.getElementById('page-' + pageId);
    if (page) page.classList.add('active');

    const nav = document.querySelector(`.nav-item[data-page="${pageId}"]`);
    if (nav) nav.classList.add('active');

    // 刷新对应页面的设备列表
    if (pageId !== 'adb_commands') {
        refreshDevices('device-select-' + pageId);
    }
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => switchPage(item.dataset.page));
});

// ========== 设备信息 ==========

async function loadDeviceInfo() {
    const serial = document.getElementById('device-select-device_info').value;
    if (!serial) return;
    const infoEl = document.getElementById('device-info-content');
    infoEl.innerHTML = '<div class="spinner"></div> 正在获取...';
    const res = await apiPost('/api/device/info', { serial });
    if (res.success) {
        const info = res.info;
        infoEl.innerHTML = `
            <div class="card">
                <div class="card-title">基本信息</div>
                <div class="info-grid" style="margin-top:12px">
                    <div class="info-row"><span class="info-label">设备型号</span><span class="info-value">${info.model || '未知'}</span></div>
                    <div class="info-row"><span class="info-label">设备品牌</span><span class="info-value">${info.brand || '未知'}</span></div>
                    <div class="info-row"><span class="info-label">序列号</span><span class="info-value">${info.serial || '未知'}</span></div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">系统信息</div>
                <div class="info-grid" style="margin-top:12px">
                    <div class="info-row"><span class="info-label">Android版本</span><span class="info-value">${info.android_version || '未知'}</span></div>
                    <div class="info-row"><span class="info-label">SDK版本</span><span class="info-value">${info.sdk_version || '未知'}</span></div>
                    <div class="info-row"><span class="info-label">分辨率</span><span class="info-value">${info.resolution || '未知'}</span></div>
                    <div class="info-row"><span class="info-label">电池电量</span><span class="info-value">${info.battery || '未知'}</span></div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">硬件信息</div>
                <div class="info-grid" style="margin-top:12px">
                    <div class="info-row"><span class="info-label">CPU架构</span><span class="info-value">${info.cpu_abi || '未知'}</span></div>
                </div>
            </div>
        `;
    }
}

// ========== 安装游戏 ==========

async function installApk() {
    const serial = document.getElementById('device-select-install_game').value;
    const apkInput = document.getElementById('apk-path');
    const apkPath = apkInput.value.trim();
    if (!serial) return showToast('请先连接设备', 'error');
    if (!apkPath) return showToast('请输入 APK 路径', 'error');

    const btn = document.getElementById('btn-install');
    btn.disabled = true;
    showLoading('install-progress');
    document.getElementById('install-status').textContent = '正在安装...';

    const res = await apiPost('/api/install', { serial, apk_path: apkPath });
    hideLoading('install-progress');
    btn.disabled = false;

    if (res.success) {
        document.getElementById('install-status').textContent = '安装成功';
        showToast('安装成功', 'success');
    } else {
        document.getElementById('install-status').textContent = '安装失败: ' + (res.stderr || res.error);
        showToast('安装失败', 'error');
    }
}

// ========== 文件管理 ==========

let currentPath = '/sdcard/';

async function loadFiles(path) {
    const serial = document.getElementById('device-select-file_manager').value;
    if (!serial) return;
    if (path) currentPath = path;

    document.getElementById('file-path').value = currentPath;
    const listEl = document.getElementById('file-list');
    listEl.innerHTML = '<div class="spinner"></div> 加载中...';

    const res = await apiPost('/api/files', { serial, path: currentPath });
    if (res.success) {
        currentPath = res.path;
        document.getElementById('file-path').value = currentPath;
        listEl.innerHTML = '';
        res.files.forEach(f => {
            const div = document.createElement('div');
            div.className = 'file-item';
            const isDir = f.trim().startsWith('d');
            div.innerHTML = `<span class="file-icon">${isDir ? '📁' : '📄'}</span> ${f}`;
            div.addEventListener('click', () => {
                document.querySelectorAll('.file-item').forEach(e => e.classList.remove('selected'));
                div.classList.add('selected');
            });
            div.addEventListener('dblclick', () => {
                if (isDir) {
                    const parts = f.trim().split(/\s+/);
                    const name = parts.slice(8).join(' ') || parts[parts.length - 1];
                    loadFiles(currentPath.replace(/\/$/, '') + '/' + name + '/');
                }
            });
            listEl.appendChild(div);
        });
    }
}

function goUpDir() {
    if (currentPath === '/') return;
    const parent = currentPath.replace(/\/$/, '').split('/').slice(0, -1).join('/') || '/';
    loadFiles(parent + '/');
}

function getSelectedFile() {
    const el = document.querySelector('.file-item.selected');
    if (!el) return null;
    const parts = el.textContent.trim().split(/\s+/);
    const name = parts.slice(9).join(' ') || parts[parts.length - 1];
    return { name, fullPath: currentPath.replace(/\/$/, '') + '/' + name };
}

async function deleteSelectedFile() {
    const serial = document.getElementById('device-select-file_manager').value;
    if (!serial) return showToast('请先连接设备', 'error');
    const file = getSelectedFile();
    if (!file) return showToast('请先选择文件', 'error');
    if (!confirm(`确定要删除 "${file.name}" 吗？`)) return;

    const res = await apiPost('/api/file/delete', { serial, path: file.fullPath });
    if (res.success) {
        showToast('删除成功', 'success');
        loadFiles();
    } else {
        showToast('删除失败', 'error');
    }
}

// ========== Root ==========

async function checkRoot() {
    const serial = document.getElementById('device-select-root').value;
    if (!serial) return showToast('请先连接设备', 'error');
    const res = await apiPost('/api/root/status', { serial });
    const el = document.getElementById('root-status-display');
    if (res.success && res.status.rooted) {
        el.innerHTML = '<span style="font-size:48px">✅</span><p style="color:#00E676;margin-top:10px">设备已Root</p>';
    } else {
        el.innerHTML = '<span style="font-size:48px">🔒</span><p style="color:#FFD740;margin-top:10px">设备未Root</p>';
    }
}

async function enableRoot() {
    const serial = document.getElementById('device-select-root').value;
    if (!serial) return showToast('请先连接设备', 'error');
    const res = await apiPost('/api/root/enable', { serial });
    if (res.success) {
        showToast('ADB Root 已启用', 'success');
        checkRoot();
    } else {
        showToast('启用失败: ' + (res.stderr || ''), 'error');
    }
}

async function execShellCmd() {
    const serial = document.getElementById('device-select-root').value;
    if (!serial) return showToast('请先连接设备', 'error');
    const cmd = document.getElementById('shell-cmd').value.trim();
    if (!cmd) return;
    const res = await apiPost('/api/shell', { serial, cmd });
    document.getElementById('root-output').textContent = res.stdout || res.stderr || '';
}

// ========== VR 投屏 ==========

async function takeScreenshot() {
    const serial = document.getElementById('device-select-vr_screen').value;
    if (!serial) return showToast('请先连接设备', 'error');
    const savePath = prompt('请输入保存路径（含文件名，如 D:\\screenshot.png）', 'yvr_screenshot.png');
    if (!savePath) return;
    const res = await apiPost('/api/screenshot', { serial, save_path: savePath });
    if (res.success) {
        showToast('截图已保存到: ' + savePath, 'success');
    } else {
        showToast('截图失败: ' + (res.stderr || ''), 'error');
    }
}

// ========== ADB 命令 ==========

function setQuickCmd(cmd) {
    document.getElementById('adb-cmd-input').value = cmd;
}

async function execAdbCmd() {
    const serial = document.getElementById('device-select-adb_commands').value;
    const cmd = document.getElementById('adb-cmd-input').value.trim();
    if (!cmd) return;
    const res = await apiPost('/api/adb', { serial, cmd });
    const output = document.getElementById('adb-output');
    output.textContent = res.success ? res.stdout : ('错误:\n' + (res.stderr || res.error));
}

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
    switchPage('device_info');
});