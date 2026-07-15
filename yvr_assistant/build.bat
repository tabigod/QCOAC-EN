@echo off
chcp 65001 >nul
echo ============================================
echo   YVR助手 - 打包构建脚本
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [1/4] 安装依赖...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/4] 准备 ADB 文件...
if not exist "adb\adb.exe" (
    echo [提示] 请将 adb.exe 及相关文件放入 adb 目录
    echo        下载地址: https://developer.android.com/tools/releases/platform-tools
    mkdir adb 2>nul
)

echo.
echo [3/4] 开始打包...
pyinstaller --noconfirm --onefile --windowed ^
    --name "YVR助手" ^
    --add-data "adb;adb" ^
    --icon=NONE ^
    --clean ^
    main.py

echo.
echo [4/4] 打包完成！
echo.
echo 输出文件: dist\YVR助手.exe
echo.
echo 请将 adb 目录复制到 dist\ 目录下，与 YVR助手.exe 同级
echo.

REM 复制 adb 到输出目录
if exist "adb\adb.exe" (
    echo 正在复制 ADB 文件到输出目录...
    xcopy /E /I /Y adb dist\adb
    echo ADB 文件已复制
)

echo.
echo ============================================
echo   打包完成！运行 dist\YVR助手.exe 启动
echo ============================================
pause