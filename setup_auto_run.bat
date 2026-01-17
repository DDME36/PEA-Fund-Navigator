@echo off
chcp 65001 >nul
cd /d "%~dp0"

cls
echo ========================================
echo   Setup Auto Run
echo ========================================
echo.
echo This will run update automatically when you login
echo.
echo Options:
echo   1. Enable Auto Run (update only)
echo   2. Enable Auto Run + Auto Push to GitHub
echo   3. Disable Auto Run
echo   4. Cancel
echo.
set /p choice="Choose (1-4): "

if "%choice%"=="1" goto ENABLE
if "%choice%"=="2" goto ENABLE_PUSH
if "%choice%"=="3" goto DISABLE
goto END

:ENABLE
echo.
echo Creating task...
schtasks /Create /TN "PEA Fund Update" /TR "%~dp0update.bat auto" /SC ONLOGON /F /RL HIGHEST
if errorlevel 1 (
    echo ERROR: Failed to create task
    echo.
    echo Try running as Administrator:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    pause
    goto END
)

REM Remove auto push flag
if exist ".auto_push" del .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run enabled!
echo ========================================
echo.
echo Will run automatically when you login
echo (Update only, no push to GitHub)
echo.
echo To verify:
echo 1. Press Win+R
echo 2. Type: taskschd.msc
echo 3. Look for "PEA Fund Update"
pause
goto END

:ENABLE_PUSH
echo.
echo Creating task...
schtasks /Create /TN "PEA Fund Update" /TR "%~dp0update.bat auto" /SC ONLOGON /F /RL HIGHEST
if errorlevel 1 (
    echo ERROR: Failed to create task
    echo.
    echo Try running as Administrator:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    pause
    goto END
)

REM Create auto push flag
echo 1 > .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run + Push enabled!
echo ========================================
echo.
echo Will run automatically when you login
echo And push to GitHub (update Vercel)
echo.
echo To verify:
echo 1. Press Win+R
echo 2. Type: taskschd.msc
echo 3. Look for "PEA Fund Update"
pause
goto END

:DISABLE
echo.
echo Removing task...
schtasks /Delete /TN "PEA Fund Update" /F
if errorlevel 1 (
    echo WARNING: Task not found or already removed
) else (
    echo OK: Task removed
)

REM Remove auto push flag
if exist ".auto_push" del .auto_push

echo.
echo ========================================
echo SUCCESS: Auto Run disabled!
echo ========================================
pause
goto END

:END
exit
