@echo off
setlocal
pushd "%~dp0"
title Topological Sort - Install Dependencies

where py >nul 2>nul
if errorlevel 1 goto :python_missing

py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if errorlevel 1 goto :python_missing

echo [1/2] Checking pip...
if not exist ".venv\Scripts\python.exe" (
    echo Creating isolated Python environment...
    py -3.12 -m venv .venv
    if errorlevel 1 goto :install_failed
)

set "APP_PYTHON=%CD%\.venv\Scripts\python.exe"
"%APP_PYTHON%" -m pip --version
if errorlevel 1 goto :install_failed

echo.
echo [2/2] Installing application dependencies...
"%APP_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto :install_failed

"%APP_PYTHON%" -c "import PySide6, networkx, matplotlib"
if errorlevel 1 goto :install_failed

echo.
echo Installation completed successfully.
echo Double-click run_app.bat or the Chinese launch file to start the application.
echo.
pause
popd
exit /b 0

:python_missing
echo.
echo Python 3.12 was not found.
echo Install Python 3.12 and enable the Python Launcher, then try again.
echo.
pause
popd
exit /b 1

:install_failed
echo.
echo Dependency installation failed. Review the error messages above.
echo Check the network connection and Python 3.12, then try again.
echo.
pause
popd
exit /b 1
