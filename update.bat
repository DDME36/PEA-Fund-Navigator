@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ถ้ารันด้วย argument (จาก Task Scheduler) ให้รันอัตโนมัติ
if not "%1"=="" goto AUTO_RUN

:MENU
cls
echo ========================================
echo   PEA Fund Navigator - Update Tool
echo ========================================
echo.
echo   1. Test (ทดสอบว่าทำงานหรือไม่)
echo   2. Update (อัพเดทข้อมูล)
echo   3. Update + Push to GitHub
echo   4. Setup Git (ครั้งแรก)
echo   5. Setup Auto Run (รันอัตโนมัติตอนเปิดเครื่อง)
echo   6. Exit
echo.
echo ========================================
set /p choice="เลือก (1-6): "

if "%choice%"=="1" goto TEST
if "%choice%"=="2" goto UPDATE
if "%choice%"=="3" goto UPDATE_PUSH
if "%choice%"=="4" goto SETUP_GIT
if "%choice%"=="5" goto SETUP_AUTO
if "%choice%"=="6" goto END
goto MENU

REM ========================================
REM AUTO RUN (จาก Task Scheduler)
REM ========================================
:AUTO_RUN
if not exist "logs" mkdir logs
set LOG_FILE=logs\auto_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo Running auto update... > "%LOG_FILE%"
echo. >> "%LOG_FILE%"
python scripts\daily_update.py >> "%LOG_FILE%" 2>&1

REM ถ้าเปิด AUTO_PUSH ให้ push อัตโนมัติ
if exist ".auto_push" (
    echo. >> "%LOG_FILE%"
    echo Pushing to GitHub... >> "%LOG_FILE%"
    git add frontend\public\data\prediction.json >> "%LOG_FILE%" 2>&1
    git commit -m "Auto update: %date% %time%" >> "%LOG_FILE%" 2>&1
    git push >> "%LOG_FILE%" 2>&1
)

exit

REM ========================================
REM TEST
REM ========================================
:TEST
cls
echo ========================================
echo   Testing...
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    goto MENU
)
echo OK: Python found
echo.

echo [2/4] Checking packages...
python -c "import pandas, numpy, yfinance, xgboost, sklearn" 2>nul
if errorlevel 1 (
    echo ERROR: Some packages missing!
    echo Run: pip install -r requirements.txt
    pause
    goto MENU
)
echo OK: All packages installed
echo.

echo [3/4] Checking files...
if not exist "scripts\daily_update.py" (
    echo ERROR: daily_update.py not found!
    pause
    goto MENU
)
echo OK: Files found
echo.

echo [4/4] Running update test...
python scripts\daily_update.py
if errorlevel 1 (
    echo ERROR: Update failed!
    pause
    goto MENU
)

echo.
echo ========================================
echo SUCCESS: Test completed!
echo ========================================
if exist "frontend\public\data\prediction.json" (
    echo Output: frontend\public\data\prediction.json
)
pause
goto MENU

REM ========================================
REM UPDATE
REM ========================================
:UPDATE
cls
echo ========================================
echo   Updating...
echo ========================================
echo.

if not exist "logs" mkdir logs
set LOG_FILE=logs\update_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo Running daily_update.py...
echo Log: %LOG_FILE%
echo.

python scripts\daily_update.py
set ERROR_LEVEL=%errorlevel%

REM Save log
python scripts\daily_update.py > "%LOG_FILE%" 2>&1

if %ERROR_LEVEL% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Update failed!
    echo ========================================
    echo Check log: %LOG_FILE%
    type "%LOG_FILE%"
    pause
    goto MENU
)

echo.
echo ========================================
echo SUCCESS: Update completed!
echo ========================================
echo Log: %LOG_FILE%
pause
goto MENU

REM ========================================
REM UPDATE + PUSH
REM ========================================
:UPDATE_PUSH
cls
echo ========================================
echo   Update + Push to GitHub
echo ========================================
echo.

echo [1/2] Running update...
python scripts\daily_update.py
if errorlevel 1 (
    echo ERROR: Update failed!
    pause
    goto MENU
)
echo OK: Update completed
echo.

echo [2/2] Pushing to GitHub...
if not exist "frontend\public\data\prediction.json" (
    echo ERROR: prediction.json not found!
    pause
    goto MENU
)

git add frontend\public\data\prediction.json
git commit -m "Daily update: %date% %time%"
if errorlevel 1 (
    echo WARNING: No changes to commit
) else (
    git push
    if errorlevel 1 (
        echo ERROR: Push failed!
        echo Run "Setup Git" first (option 4)
        pause
        goto MENU
    )
    echo OK: Pushed to GitHub!
    echo Vercel will deploy in ~2 minutes
)

echo.
echo ========================================
echo SUCCESS: Done!
echo ========================================
pause
goto MENU

REM ========================================
REM SETUP GIT
REM ========================================
:SETUP_GIT
cls
echo ========================================
echo   Git Setup
echo ========================================
echo.

echo [1/4] Checking Git...
git --version
if errorlevel 1 (
    echo ERROR: Git not found!
    echo Install: winget install Git.Git
    pause
    goto MENU
)
echo OK: Git found
echo.

echo [2/4] Checking repository...
git status >nul 2>&1
if errorlevel 1 (
    echo Initializing Git...
    git init
    echo OK: Git initialized
) else (
    echo OK: Already a Git repository
)
echo.

echo [3/4] Checking remote...
git remote -v | find "origin" >nul
if errorlevel 1 (
    echo.
    set /p REPO_URL="Enter GitHub repository URL: "
    git remote add origin %REPO_URL%
    echo OK: Remote added
) else (
    echo OK: Remote configured
)
echo.

echo [4/4] Setting up credentials...
git config credential.helper store
echo OK: Credential helper configured
echo.

echo Testing push...
git add .gitignore
git commit -m "Test" --allow-empty
git push -u origin main
if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Use Personal Access Token:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Generate new token (classic)
    echo 3. Select: repo (all)
    echo 4. Use token as password
    echo.
    echo Or use GitHub CLI:
    echo   winget install GitHub.cli
    echo   gh auth login
    pause
    goto MENU
)

echo.
echo ========================================
echo SUCCESS: Git setup completed!
echo ========================================
pause
goto MENU

REM ========================================
REM SETUP AUTO RUN
REM ========================================
:SETUP_AUTO
cls
echo ========================================
echo   Setup Auto Run
echo ========================================
echo.
echo This will run update automatically when you login
echo.
echo Options:
echo   1. Enable Auto Run (on login)
echo   2. Enable Auto Run + Auto Push to GitHub
echo   3. Disable Auto Run
echo   4. Cancel
echo.
set /p auto_choice="Choose (1-4): "

if "%auto_choice%"=="1" goto AUTO_ENABLE
if "%auto_choice%"=="2" goto AUTO_ENABLE_PUSH
if "%auto_choice%"=="3" goto AUTO_DISABLE
goto MENU

:AUTO_ENABLE
echo.
echo Creating task...
schtasks /Create /TN "PEA Fund Update" /TR "\"%~dp0update.bat\" auto" /SC ONLOGON /F /RL HIGHEST
if errorlevel 1 (
    echo ERROR: Failed to create task
    pause
    goto MENU
)

REM ลบ flag auto push
if exist ".auto_push" del .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run enabled!
echo ========================================
echo.
echo Will run automatically when you login
echo (Update only, no push to GitHub)
pause
goto MENU

:AUTO_ENABLE_PUSH
echo.
echo Creating task...
schtasks /Create /TN "PEA Fund Update" /TR "\"%~dp0update.bat\" auto" /SC ONLOGON /F /RL HIGHEST
if errorlevel 1 (
    echo ERROR: Failed to create task
    pause
    goto MENU
)

REM สร้าง flag auto push
echo 1 > .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run + Push enabled!
echo ========================================
echo.
echo Will run automatically when you login
echo And push to GitHub (update Vercel)
pause
goto MENU

:AUTO_DISABLE
echo.
echo Removing task...
schtasks /Delete /TN "PEA Fund Update" /F
if errorlevel 1 (
    echo WARNING: Task not found or already removed
)

REM ลบ flag auto push
if exist ".auto_push" del .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run disabled!
echo ========================================
pause
goto MENU

REM ========================================
REM END
REM ========================================
:END
exit
