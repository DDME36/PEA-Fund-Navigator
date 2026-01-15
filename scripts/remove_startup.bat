@echo off
chcp 65001 >nul
title Remove PEA Fund Navigator Startup

set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PEA_Fund_Update.lnk"

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo [OK] ลบการรันอัตโนมัติแล้ว
) else (
    echo [INFO] ไม่พบการตั้งค่ารันอัตโนมัติ
)

pause
