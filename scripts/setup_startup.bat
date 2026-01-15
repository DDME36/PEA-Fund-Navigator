@echo off
chcp 65001 >nul
title Setup PEA Fund Navigator Startup

echo ========================================
echo   ตั้งค่าให้รันอัตโนมัติตอนเปิดคอม
echo ========================================
echo.

:: สร้าง shortcut ใน Startup folder
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_PATH=%~dp0auto_update.bat"
set "SHORTCUT=%STARTUP%\PEA_Fund_Update.lnk"

:: ใช้ PowerShell สร้าง shortcut
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%SCRIPT_PATH%'; $s.WorkingDirectory = '%~dp0..'; $s.WindowStyle = 7; $s.Save()"

if exist "%SHORTCUT%" (
    echo [OK] ตั้งค่าสำเร็จ!
    echo.
    echo Shortcut ถูกสร้างที่:
    echo %SHORTCUT%
    echo.
    echo ทุกครั้งที่เปิดคอม จะรันอัพเดทอัตโนมัติ
) else (
    echo [ERROR] ไม่สามารถสร้าง shortcut ได้
)

echo.
pause
