@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo      advisor-finder  Uninstall
echo ========================================
echo.
echo This will delete the virtual environment and downloaded browser.
echo Your personal files and results will NOT be deleted.
echo.
set /p CONFIRM=Type "yes" to confirm:

if /i not "%CONFIRM%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [1/2] Removing virtual environment...
if exist "venv" (
    rmdir /s /q venv
    echo Done.
) else (
    echo Not found, skipping.
)

echo.
echo [2/2] Removing Playwright browsers...
if exist "%USERPROFILE%\AppData\Local\ms-playwright" (
    rmdir /s /q "%USERPROFILE%\AppData\Local\ms-playwright"
    echo Done.
) else (
    echo Not found, skipping.
)

echo.
echo ========================================
echo Uninstall complete.
echo ========================================
echo.
echo Press any key to exit...
pause >nul
