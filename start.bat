@echo off
REM Quick Start Script for Trading Bot
REM This script helps you get started quickly

echo.
echo ========================================
echo   TRADING BOT - QUICK START
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import ccxt" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Dependencies not found. Installing...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ========================================
echo   SELECT MODE
echo ========================================
echo.
echo 1. Start Web Dashboard (Recommended for first-time users)
echo 2. Run Backtesting
echo 3. Start Live Trading (Paper Mode)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto backtest
if "%choice%"=="3" goto live
if "%choice%"=="4" goto end

echo Invalid choice
pause
exit /b 1

:dashboard
echo.
echo Starting Web Dashboard...
echo Dashboard will open automatically in your browser
echo.
cd backend
python web_server.py
goto end

:backtest
echo.
echo Running Backtesting Mode...
echo.
cd backend
python -c "from main import TradingBot; bot = TradingBot(); bot.run_backtest()"
pause
goto end

:live
echo.
echo ========================================
echo   WARNING: LIVE TRADING MODE
echo ========================================
echo.
echo Current mode: PAPER TRADING (Safe)
echo.
echo To enable real trading:
echo 1. Edit config.yaml
echo 2. Change 'trading_mode' to 'live'
echo 3. Add your API keys
echo.
echo Starting bot in PAPER mode...
echo.
cd backend
python main.py
goto end

:end
echo.
echo Thank you for using Trading Bot!
pause
