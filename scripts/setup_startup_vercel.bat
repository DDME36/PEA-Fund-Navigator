@echo off
chcp 65001 >nul
title Setup PEA Fund Navigator - Vercel Mode

echo ========================================
echo   ตั้งค่าให้รัน + Push อัตโนมัติ
echo   (สำหรับใช้กับ Vercel)
echo ========================================
echo.

:: สร้าง shortcut ใน Startup folder
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_PATH=%~dp0update_and_push.bat"
set "SHORTCUT=%STARTUP%\PEA_Fund_Update.lnk"

:: ใช้ PowerShell สร้าง shortcut
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%SCRIPT_PATH%'; $s.WorkingDirectory = '%~dp0..'; $s.WindowStyle = 7; $s.Save()"

if exist "%SHORTCUT%" (
    echo [OK] ตั้งค่าสำเร็จ!
    echo.
    echo ทุกครั้งที่เปิดคอม:
    echo   1. รัน daily_update.py
    echo   2. Commit และ Push ไป GitHub
    echo   3. Vercel จะ deploy อัตโนมัติ
    echo.
    echo หมายเหตุ: ต้อง login git ไว้ก่อน
) else (
    echo [ERROR] ไม่สามารถสร้าง shortcut ได้
)

echo.
pause
