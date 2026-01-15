@echo off
REM ============================================
REM PEA PVD Navigator - Run Script
REM ============================================

echo.
echo ========================================
echo    PEA PVD Navigator
echo ========================================
echo.

if "%1"=="" (
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   backend   - Start backend API server
    echo   frontend  - Start frontend dev server
    echo   train     - Train ML model
    echo   predict   - Get current prediction
    echo   all       - Start both backend and frontend
    echo.
    goto :eof
)

if "%1"=="backend" (
    echo Starting Backend API...
    python -m uvicorn app.main:app --reload --port 8000
    goto :eof
)

if "%1"=="frontend" (
    echo Starting Frontend...
    cd frontend
    npm run dev
    goto :eof
)

if "%1"=="train" (
    echo Training ML Model...
    python -c "from app.main import monthly_predictor; from app.data_fetcher import fetch_stock_data; from app.monthly_ml import create_monthly_data_for_ml; from app.config import TICKER; df = fetch_stock_data(TICKER); monthly = create_monthly_data_for_ml(df); print(monthly_predictor.train(monthly))"
    goto :eof
)

if "%1"=="predict" (
    echo Getting Prediction...
    python scripts/predict.py
    goto :eof
)

if "%1"=="all" (
    echo Starting Backend and Frontend...
    start cmd /k "python -m uvicorn app.main:app --reload --port 8000"
    timeout /t 3 >nul
    cd frontend
    npm run dev
    goto :eof
)

echo Unknown command: %1
