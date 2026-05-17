# 以管理员身份运行此脚本
# 功能：断开当前Microsoft账户的绑定，清理凭据和注册表关联

Write-Host "正在清理Microsoft账户关联..." -ForegroundColor Cyan

# 1. 断开工作或学校账户（如果有）
$workAccounts = Get-WmiObject -Class Win32_UserAccount | Where-Object {$_.Domain -ne $env:COMPUTERNAME}
foreach ($acc in $workAccounts) {
    Write-Host "断开工作/学校账户: $($acc.Name)" -ForegroundColor Yellow
    # 使用 dsregcmd 命令退出Azure AD/工作区
    & dsregcmd /leave
}

# 2. 清理凭据管理器中的微软账户项
cmdkey /list | ForEach-Object {
    if ($_ -match "MicrosoftAccount|live|outlook|hotmail|msn") {
        $target = ($_ -split ":")[1].Trim()
        if ($target) {
            Write-Host "删除凭据: $target" -ForegroundColor Yellow
            cmdkey /delete:$target
        }
    }
}

# 3. 删除注册表中当前用户的微软账户关联
$paths = @(
    "HKCU:\Software\Microsoft\IdentityCRL\UserExtendedProperties",
    "HKCU:\Software\Microsoft\IdentityCRL\StoredIdentities",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CredentialProvider"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "清理注册表: $path" -ForegroundColor Yellow
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# 4. 删除当前用户的微软账户令牌
$tokenPath = "$env:LOCALAPPDATA\Microsoft\TokenBroker"
if (Test-Path $tokenPath) {
    Write-Host "删除TokenBroker缓存" -ForegroundColor Yellow
    Remove-Item -Path $tokenPath -Recurse -Force
}

Write-Host "`n清理完成！正在重启 Explorer 和 TokenBroker 服务..." -ForegroundColor Green
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 5. 提示用户手动切换到本地账户
Write-Host "`n请按以下步骤操作：" -ForegroundColor Cyan
Write-Host "1. 打开 设置 -> 账户 -> 你的信息" -ForegroundColor White
Write-Host "2. 点击“改用本地账户登录”并按照提示设置本地用户名和密码" -ForegroundColor White
Write-Host "`n如果“改用本地账户登录”按钮仍然灰色，请重启电脑后再试。" -ForegroundColor Yellow
