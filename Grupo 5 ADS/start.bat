@echo off
chcp 65001 >nul
title Mini Provas
echo =================================
echo       Mini Provas - Iniciando
echo =================================
echo.
cd /d "%~dp0"
python run.py
echo.
echo Servidor encerrado.
pause
