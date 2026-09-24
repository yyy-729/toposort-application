@echo off
setlocal
set "APP_PYTHONW=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%APP_PYTHONW%" goto :dependencies_missing

start "" "%APP_PYTHONW%" "%~dp0run_app.pyw"
exit /b 0

:dependencies_missing
echo.
echo Application environment is missing. Run install_dependencies.bat first.
echo.
pause
exit /b 1
