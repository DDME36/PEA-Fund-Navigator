@echo off
chcp 65001 >nul
title PEA Fund Navigator - Update & Push to GitHub

echo ========================================
echo   PEA Fund Navigator - Update & Push
echo ========================================
echo.

:: ไปที่ root ของโปรเจค
cd /d "%~dp0.."

:: ตรวจสอบว่ารันไปแล้ววันนี้หรือยัง
set "LOCK_FILE=%TEMP%\pea_fund_push_%DATE:~-10,2%%DATE:~-7,2%%DATE:~-4,4%.lock"
if exist "%LOCK_FILE%" (
    echo [INFO] วันนี้ push ไปแล้ว ข้ามการอัพเดท
    timeout /t 3 >nul
    exit /b 0
)

echo [1/4] กำลังอัพเดทข้อมูล...
python scripts/daily_update.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] อัพเดทล้มเหลว!
    msg * "PEA Fund Navigator: อัพเดทล้มเหลว"
    pause
    exit /b 1
)

echo.
echo [2/4] กำลัง git add...
git add frontend/public/data/prediction.json

echo.
echo [3/4] กำลัง git commit...
git commit -m "📊 Daily update: %DATE%"

echo.
echo [4/4] กำลัง git push...
git push origin main

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Push ล้มเหลว!
    msg * "PEA Fund Navigator: Push ล้มเหลว กรุณาตรวจสอบ"
    pause
    exit /b 1
)

:: สร้าง lock file
echo %DATE% %TIME% > "%LOCK_FILE%"

echo.
echo ========================================
echo   อัพเดทและ Push สำเร็จ!
echo   Vercel จะ deploy อัตโนมัติ
echo ========================================
timeout /t 5 >nul
exit /b 0
