# dev_logout.py
# 退登诸如VS Code、Visual Studio与Git等与开发有关的软件
from ..util import Category,Item
from ..util import dispatch,invoke,unlink

dev_cat = Category("开发")
# Git
# 为简明起见，直接将应用名作为变量名
git = Item(dev_cat, "Git")

@git.add_strategy("删除配置文件")
def git_delete_config(item):
    """删除Git配置文件"""
    # 直接删除配置文件即可
    config_path = r"C:\Users\{username}\.gitconfig".format(username=invoke("get_username"))
    unlink(config_path)

@git.add_strategy("使用Git命令退登")
def git_logout(item):
    """使用Git命令退登"""
    # 直接使用Git命令退登
    invoke("git credential-manager uninstall")

# Visual Studio Code
vscode = Item(dev_cat, "Visual Studio Code")

@vscode.add_strategy("删除配置文件")
def vscode_delete_config(item):
    """删除VS Code配置文件"""
    # 直接删除配置文件即可
    config_path = r"C:\Users\{username}\AppData\Roaming\Code".format(username=invoke("get_username"))
    unlink(config_path)