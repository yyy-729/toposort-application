@echo off
setlocal
pushd "%~dp0"
title Topological Sort Application

where py >nul 2>nul
if errorlevel 1 goto :python_missing

py -3.12 -c "import PySide6, networkx, matplotlib" >nul 2>nul
if errorlevel 1 goto :dependencies_missing

set "PYTHONPATH=%CD%\src"
py -3.12 -m toposort_app
set "APP_EXIT_CODE=%ERRORLEVEL%"

if not "%APP_EXIT_CODE%"=="0" goto :app_failed

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

:dependencies_missing
echo.
echo Application dependencies are missing.
echo Run install_dependencies.bat first, then try again.
echo.
pause
popd
exit /b 1

:app_failed
echo.
echo The application stopped with error code %APP_EXIT_CODE%.
echo Review the Python error messages above before closing this window.
echo.
pause
popd
exit /b %APP_EXIT_CODE%

