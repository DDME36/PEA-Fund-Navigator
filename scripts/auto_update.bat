@echo off
chcp 65001 >nul
title PEA Fund Navigator - Daily Update

echo ========================================
echo   PEA Fund Navigator - Daily Update
echo ========================================
echo.

:: ตรวจสอบว่ารันไปแล้ววันนี้หรือยัง
set "LOCK_FILE=%TEMP%\pea_fund_update_%DATE:~-10,2%%DATE:~-7,2%%DATE:~-4,4%.lock"
if exist "%LOCK_FILE%" (
    echo [INFO] วันนี้รันไปแล้ว ข้ามการอัพเดท
    timeout /t 3 >nul
    exit /b 0
)

:: หา Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] ไม่พบ Python กรุณาติดตั้ง Python ก่อน
    msg * "PEA Fund Navigator: ไม่พบ Python กรุณาติดตั้ง Python"
    pause
    exit /b 1
)

:: ไปที่ root ของโปรเจค
cd /d "%~dp0.."

echo [1/3] กำลังตรวจสอบ dependencies...
pip install -r requirements.txt -q

echo [2/3] กำลังอัพเดทข้อมูล...
python scripts/daily_update.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] อัพเดทล้มเหลว!
    msg * "PEA Fund Navigator: อัพเดทล้มเหลว กรุณาตรวจสอบ"
    pause
    exit /b 1
)

:: สร้าง lock file
echo %DATE% %TIME% > "%LOCK_FILE%"

echo.
echo [3/3] อัพเดทสำเร็จ!
echo ========================================
echo   ข้อมูลถูกบันทึกที่:
echo   frontend/public/data/prediction.json
echo ========================================
timeout /t 5 >nul
exit /b 0
