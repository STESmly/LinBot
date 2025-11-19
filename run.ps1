# 设置执行策略（如果需要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# 激活虚拟环境
& ./venv/Scripts/Activate.ps1

# 切换到linbot目录并运行
Set-Location "linbot"
python run_with_reload.py

# 暂停等待
Write-Host "按任意键继续..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")