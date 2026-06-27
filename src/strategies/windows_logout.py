# windows_logout.py
# 退登Windows系统
from ..util import Category,Item
from ..util import dispatch,invoke,unlink

win_cat = Category("Windows")

# regedit
regedit = Item(win_cat, "注册表")

@regedit.add_strategy("用命令行删除凭证")
def disregcmd():
    r"""把下面的powershell语句翻译成Python即可
    `# 1. 断开工作或学校账户（如果有）
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
    `
    """
    workAccounts = invoke("Get-WmiObject -Class Win32_UserAccount | Where-Object {$_.Domain -ne $env:COMPUTERNAME}", admin=True)
    if workAccounts:
        invoke("dsregcmd /leave", admin=True)

    # 清理凭据管理器中的微软账户条目
    invoke(r'cmdkey /list | ForEach-Object { if ($_ -match "MicrosoftAccount|live|outlook|hotmail|msn") { $target = ($_ -split ":")[1].Trim(); if ($target) { cmdkey /delete:$target } } }', admin=True)

    # 删除注册表中当前用户的微软账户关联
    registry_paths = [
        r"HKCU:\Software\Microsoft\IdentityCRL\UserExtendedProperties",
        r"HKCU:\Software\Microsoft\IdentityCRL\StoredIdentities",
        r"HKCU:\Software\Microsoft\IdentityCRL\StoredIdentities",
        r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CredentialProvider",
    ]
    for path in registry_paths:
        invoke(f'Remove-Item -Path "{path}" -Recurse -Force -ErrorAction SilentlyContinue', admin=True)

    # 删除当前用户的微软账户令牌
    invoke(r'if (Test-Path "$env:LOCALAPPDATA\Microsoft\TokenBroker") { Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\TokenBroker" -Recurse -Force }', admin=True)
    
