@echo off
chcp 65001 > nul
title LUMARC HR Bot
echo ======================================================
echo           LUMARC HR TELEGRAM BOT ISHGA TUSHYAPTI
echo ======================================================
echo.

cd /d "%~dp0"

:: Python mavjudligini tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATOLIK] Kompyuteringizda Python topilmadi!
    pause
    exit /b
)

:: Kutubxonalarni tekshirish va botni ishga tushirish
python main.py

echo.
echo Bot to'xtadi.
pause
