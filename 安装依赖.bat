@echo off
chcp 65001 >nul
cd /d "%~dp0"

py -3.12 -m pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败，请检查网络和 Python 3.12。
    pause
    exit /b 1
)

echo 依赖安装完成，可以双击“启动应用.bat”运行程序。
pause

