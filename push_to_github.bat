@echo off
chcp 65001 > nul
title GitHubga yuklash (LUMARC HR Bot)
cd /d "%~dp0"
echo ======================================================
echo       LOYIHA GITHUBGA YUKLANMOQDA...
echo ======================================================
echo.

git branch -M main
git push -u origin main -f

echo.
echo ======================================================
echo Agar muvaffaqiyatli yuklangan bo'lsa, oynani yopishingiz mumkin.
echo ======================================================
pause
