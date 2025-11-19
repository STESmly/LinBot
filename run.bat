@echo off
chcp 65001 >nul
cd /d "%~dp0"
title LinBot 启动器

echo ================================
echo        LinBot 启动器
echo ================================
powershell -ExecutionPolicy Bypass -Command "& './venv/Scripts/Activate.ps1'; cd 'linbot'; python 'run_with_reload.py'; pause"