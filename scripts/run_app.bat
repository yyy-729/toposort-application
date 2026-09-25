@echo off
setlocal
pushd "%~dp0.."
title Topological Sort Application - Diagnostics

set "APP_PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%APP_PYTHON%" goto :dependencies_missing

set "PYTHONPATH=%CD%\src"
"%APP_PYTHON%" -m toposort_app
set "APP_EXIT_CODE=%ERRORLEVEL%"

if not "%APP_EXIT_CODE%"=="0" goto :app_failed

popd
exit /b 0

:dependencies_missing
echo.
echo The isolated application environment is missing or incomplete.
echo Run the install BAT in the project root first, then try again.
echo.
pause
popd
exit /b 1

:app_failed
echo.
echo The application stopped with error code %APP_EXIT_CODE%.
echo If dependencies are missing, run the install BAT in the project root first.
echo Review the Python error messages above before closing this window.
echo.
pause
popd
exit /b %APP_EXIT_CODE%
