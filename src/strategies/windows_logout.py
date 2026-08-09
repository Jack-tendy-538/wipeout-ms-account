# windows_logout.py
# 退登Windows系统
from util import Category,Item
from util import dispatch,invoke,unlink

import time,sys
from pywinauto import Application, Desktop
import tkinter.messagebox as messagebox

win_cat = Category("Windows")

# regedit
regedit = Item(win_cat, "注册表",links={"文档": "https://docs.microsoft.com/zh-cn/windows/win32/sysinfo/registry-functions"})

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
    
# msedge
msedge = Item(win_cat, "Microsoft Edge",links={"文档": "https://learn.microsoft.com/zh-cn/microsoft-edge/"
                                               ,"讨论":"https://forum.smart-teach.cn/d/2082-ru-he-che-di-tui-chu-edgezhang-hao-bing-qing-chu-deng-lu-hen-ji/16"})

@msedge.add_strategy(r"%localappdata%\Microsoft\路径下找到IdentityCache和OneAuth两个文件夹删除")
def delete_edge_identity_cache():
    """删除 Edge 的 IdentityCache 和 OneAuth 文件夹"""
    local_appdata = dispatch("WScript.Shell").ExpandEnvironmentStrings(r"%localappdata%")
    edge_path = f"{local_appdata}\\Microsoft\\Edge\\User Data\\Default"
    identity_cache_path = f"{edge_path}\\IdentityCache"
    oneauth_path = f"{edge_path}\\OneAuth"

    # 删除 IdentityCache 文件夹
    unlink(identity_cache_path)
    # 删除 OneAuth 文件夹
    unlink(oneauth_path)

# 以word为代表的office应用程序，退登需要通过UI操作
word = Item(win_cat, "Microsoft Word",links={"文档": "https://learn.microsoft.com/zh-cn/office/dev/add-ins/word/"})

def ensure_word_visible():
    word = dispatch("Word.Application")
    # 如果未启动，会启动一个实例；如果已启动，会连接现有实例
    word.Visible = True
    return word

@word.add_strategy("从GUI中退登")
def sign_out_word():
    word = ensure_word_visible()
    # 等待 UI 起来
    time.sleep(1.5)

    # 通过可访问性 (UIA) 后端连接到正在运行的 WINWORD 进程
    app = Application(backend="uia").connect(path="WINWORD.EXE")
    # 获取桌面视图，方便查找元素
    desktop = Desktop(backend="uia")

    # 找到 Word 主窗口（标题可能因文档不同而不同）。使用类名 OpusApp 更通用。
    try:
        main = desktop.window(class_name="OpusApp")
    except Exception:
        # 如果找不到主窗口，列出所有顶层窗口帮助调试
        messagebox.showerror("未找到 Word 主窗口","没有找到 Word 主窗口，请用 Inspect.exe 检查 ClassName/Title。")
        raise RuntimeError("未找到 Word 主窗口")

    # 进入 File 后台页：File 按钮通常是名为 "File" 或 "File Tab" 的元素
    # 如果下面两个名字都找不到，请用 Inspect.exe 查看实际名称并替换 title=...
    for file_title in ("File", "File Tab"):
        try:
            file_btn = main.child_window(title=file_title, control_type="Button")
            if file_btn.exists(timeout=1):
                file_btn.click_input()
                break
        except Exception:
            pass
    else:
        messagebox.showerror("未找到 File 按钮","未找到 File 按钮，请用 Inspect.exe 确认控件名称。")
        raise RuntimeError("未找到 File 按钮")

    time.sleep(0.8)
    # 在 Backstage 视图里找到 Account（帐户）项并点击
    try:
        # 有时是 ListItem、有时是 Button，使用更宽松的查找
        acct = desktop.window(control_type="Window").child_window(title="Account", control_type="ListItem")
        if not acct.exists(timeout=1):
            acct = desktop.window(control_type="Window").child_window(title="Account", control_type="Button")
        acct.click_input()
    except Exception:
        messagebox.showerror("未能在 Backstage 找到 Account","未能在 Backstage 找到 Account，可能控件名称不同，请检查并调整。")
        raise RuntimeError("未能在 Backstage 找到 Account")

    time.sleep(0.8)
    # 在 Account 页里查找 "Sign out" / "退出登录" 控件（可能是 Hyperlink 或 Button）
    try:
        signout = desktop.window(control_type="Window").child_window(title_re="Sign out|退出", control_type="Hyperlink")
        if not signout.exists(timeout=1):
            signout = desktop.window(control_type="Window").child_window(title_re="Sign out|退出", control_type="Button")
        signout.click_input()
    except Exception:
        messagebox.showerror("未找到 Sign out 控件","未找到 Sign out 控件；请用 Inspect.exe 确认实际名称（例如 'Sign out', '注销', '退出' 等）。")
        raise RuntimeError("未找到 Sign out 控件")

    # 处理可能弹出的确认对话框（标题/按钮名可能不同）
    time.sleep(0.6)
    try:
        dlg = Desktop(backend="uia").window(title_re=".*Sign out.*|.*退出登录.*|.*注销.*")
        if dlg.exists(timeout=1.5):
            yes_btn = dlg.child_window(title_re="Yes|是", control_type="Button")
            if yes_btn.exists(timeout=0.5):
                yes_btn.click_input()
    except Exception:
        # 有时没有确认对话框
        pass

    return True

# msstore
msstore = Item(win_cat, "Microsoft Store",links={"文档": "https://learn.microsoft.com/zh-cn/sysinternals/downloads/microsoft-store"})

@msstore.add_strategy("从GUI中退登")
def sign_out_msstore():
    """退出登录 Microsoft Store"""
    # 通过可访问性 (UIA) 后端连接到正在运行的 Microsoft Store 进程
    app = Application(backend="uia").connect(path="WinStore.App.exe")
    desktop = Desktop(backend="uia")

    # 找到 Microsoft Store 主窗口
    try:
        main = desktop.window(class_name="ApplicationFrameWindow", title_re=".*Microsoft Store.*")
    except Exception:
        messagebox.showerror("未找到 Microsoft Store 主窗口","没有找到 Microsoft Store 主窗口，请用 Inspect.exe 检查 ClassName/Title。")
        raise RuntimeError("未找到 Microsoft Store 主窗口")

    # 点击右上角的用户头像按钮
    try:
        profile_btn = main.child_window(title_re=".*Profile.*|.*账户.*", control_type="Button")
        profile_btn.click_input()
    except Exception:
        messagebox.showerror("未找到 Profile 按钮","未找到 Profile 按钮，请用 Inspect.exe 确认控件名称。")
        raise RuntimeError("未找到 Profile 按钮")

    time.sleep(0.8)
    # 在弹出的菜单中点击 "Sign out" / "退出登录"
    try:
        signout = desktop.window(control_type="Menu").child_window(title_re="Sign out|退出", control_type="MenuItem")
        signout.click_input()
    except Exception:
        messagebox.showerror("未找到 Sign out 菜单项","未找到 Sign out 菜单项；请用 Inspect.exe 确认实际名称。")
        raise RuntimeError("未找到 Sign out 菜单项")

    return True