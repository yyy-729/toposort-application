@echo off
chcp 65001 >nul
cd /d "%~dp0"

py -3.12 -c "import PySide6, networkx, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo 缺少运行依赖，请先双击“安装依赖.bat”。
    pause
    exit /b 1
)

set "PYTHONPATH=%CD%\src"
py -3.12 -m toposort_app

