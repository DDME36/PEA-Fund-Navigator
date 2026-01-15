@echo off
REM Daily Update Script for Windows
REM ตั้ง Task Scheduler ให้รันตอนเปิดเครื่อง

cd /d "%~dp0.."
echo Running daily update...
python scripts/daily_update.py

REM Optional: Auto push to GitHub
REM git add frontend/public/data/prediction.json
REM git commit -m "Daily update: %date%"
REM git push

pause
