@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo       advisor-finder  Setup
echo ========================================

echo.
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause & exit /b 1
)
python --version

echo.
echo [2/4] Creating virtual environment...
if exist "venv\Scripts\python.exe" (
    echo Virtual environment already exists, skipping.
) else (
    python -m venv venv
    if %errorlevel% neq 0 ( echo [ERROR] Failed to create virtual environment. & pause & exit /b 1 )
)

echo.
echo [3/4] Installing packages (this may take a few minutes)...
venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 ( echo [ERROR] Package installation failed. & pause & exit /b 1 )

echo.
echo [4/4] Installing browser for web scraping...
venv\Scripts\playwright install chromium
if %errorlevel% neq 0 ( echo [ERROR] Browser installation failed. & pause & exit /b 1 )

echo.
echo [Creating folders...]
if not exist "personal_info" mkdir "personal_info"
if not exist "results" mkdir "results"
if not exist ".env" echo DEEPSEEK_API_KEY=your_api_key_here > .env

echo.
echo ========================================
echo [DONE] Setup complete!
echo.
echo Next steps:
echo  1. Open .env, replace "your_api_key_here" with your DeepSeek API Key
echo     Get your key at: platform.deepseek.com
echo  2. Put your resume (.txt/.docx/.pdf) into: personal_info\
echo  3. Double-click start.bat to launch
echo ========================================
echo.
echo Press any key to exit...
pause >nul
