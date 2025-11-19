@echo off
chcp 65001 >nul
cd /d "%~dp0"
title LinBot 启动器

echo ================================
echo        LinBot 启动器
echo ================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

echo [信息] 检测到Python环境

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo [信息] 虚拟环境不存在，开始创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
) else (
    echo [信息] 虚拟环境已存在
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查并安装依赖
echo [信息] 检查依赖包...
if exist "requirements.txt" (
    echo [信息] 开始安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
) else (
    echo [警告] 未找到requirements.txt文件
)

REM 检查linbot目录是否存在
if not exist "linbot" (
    echo [错误] 未找到linbot目录
    pause
    exit /b 1
)

REM 运行程序
echo [信息] 启动LinBot...
cd linbot
python run_with_reload.py

REM 暂停等待
echo.
echo ================================
echo 程序已退出，按任意键关闭窗口...
pause >nul