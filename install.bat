@echo off
REM AGENT-Pro Installation Script for Windows
REM This script handles all dependencies and conflicts automatically

setlocal enabledelayedexpansion

echo ==================================================
echo   AGENT-Pro Installation Script
echo   For Windows Systems
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js found

REM Step 1: Create virtual environment
echo.
echo [*] Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [!] Virtual environment already exists
)

REM Step 2: Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Step 3: Upgrade pip, setuptools, and wheel
echo [*] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel packaging >nul 2>&1

REM Step 4: Install Python dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

REM Step 5: Install Node.js dependencies
echo [*] Installing Node.js dependencies...
npm install --legacy-peer-deps >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo [OK] Node.js dependencies installed

REM Step 6: Copy environment file
echo [*] Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo [!] Created .env file - Please edit it with your API keys
) else (
    echo [!] .env file already exists
)

REM Step 7: Verify installation
echo.
echo [*] Verifying installation...

python -c "import fastapi, pydantic, openai" >nul 2>&1
if errorlevel 1 (
    echo [X] Python packages verification failed
) else (
    echo [OK] Python packages verified
)

npm list react vite >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js packages verification failed
) else (
    echo [OK] Node.js packages verified
)

echo.
echo ==================================================
echo Installation Complete!
echo ==================================================
echo.
echo Next steps:
echo.
echo 1. Edit your environment variables:
echo    notepad .env
echo    (Add your DEEPSEEK_API_KEY)
echo.
echo 2. Start the backend (Command Prompt 1):
echo    venv\Scripts\activate.bat
echo    python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. Start the frontend (Command Prompt 2):
echo    cd client
echo    npm run dev
echo.
echo 4. Open your browser:
echo    http://localhost:5173
echo.
pause
