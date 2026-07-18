# util.py
import subprocess
import sys ,re, argparse
import urllib.parse
from dataclasses import dataclass, field
from shutil import rmtree
from os import unlink
import win32com.client
import win32event,win32process,win32con
import win32com.client.gencache as gencache
import win32com.shell.shell as shell
import requests
from typing import Any, Callable, Dict, List, Optional, Tuple
from pathlib import Path
from webbrowser import open as open_url

__ALL__ = ["Category", "Item", "BoolVar", "download_icon", "is_admin", "restart_as_admin", "invoke", "call_url","unlink","remove_tree","open_url"]

class BoolVar:
    def __init__(self, value: bool = False) -> None:
        self._value = bool(value)

    def get(self) -> bool:
        return self._value

    def set(self, value: bool) -> None:
        self._value = bool(value)

@dataclass
class Category:
    name: str
    items: List["Item"] = field(default_factory=list)
    errors: List[Tuple[str, str, str]] = field(default_factory=list)
    checked: BoolVar = field(default_factory=lambda: BoolVar(value=True))

    def __repr__(self) -> str:
        return f"Category(name={self.name!r}, items={len(self.items)}, checked={self.checked.get()})"

    def toggle(self) -> None:
        self.checked.set(not self.checked.get())
        for item in self.items:
            item.checked.set(self.checked.get())

    def add_item(self, item: "Item") -> "Item":
        self.items.append(item)
        return item

    def execute(self):
        for item in self.items:
            if item.checked.get():
                item.execute()

@dataclass
class Item:
    category: Category
    name: str
    links: Dict[str, str] = field(default_factory=dict)
    icon: Optional[str] = None
    checked: BoolVar = field(default_factory=lambda: BoolVar(value=False))
    is_error: bool = False
    strategies: List[Tuple[str, Callable[..., Any]]] = field(default_factory=list)
    use_strategy: int = 0

    def __post_init__(self) -> None:
        self.category.add_item(self)

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, checked={self.checked.get()}, strategies={len(self.strategies)})"

    def toggle(self) -> None:
        self.checked.set(not self.checked.get())

    def add_strategy(self, strategy_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            def no_traceback(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.is_error = True
                    self.category.errors.append((self.name, strategy_name, str(e)))
                    return None
            self.strategies.append((strategy_name, no_traceback))
            return no_traceback
        return wrapper

    def execute(self):
        if self.checked.get():
            if self.use_strategy < 0 or self.use_strategy >= len(self.strategies):
                raise ValueError(f"Invalid strategy index {self.use_strategy} for item {self.name}")
            strategy_name, strategy_func = self.strategies[self.use_strategy]
            return strategy_func()

# 实用函数
def download_icon(url: str, save_path: str) -> None:
    """下载图标"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path
    except Exception as e:
        raise RuntimeError(f"Failed to download icon from '{url}': {e}")
def is_admin():
    try:
        return shell.IsUserAnAdmin()
    except Exception:
        return False

def restart_as_admin():
    # 重启自己并请求管理员权限（会弹出 UAC）
    params = " ".join(['"%s"' % (x,) for x in sys.argv])
    procInfo = shell.ShellExecuteEx(lpVerb='runas',
                                   lpFile=sys.executable,
                                   lpParameters=params,
                                   nShow=win32con.SW_SHOWNORMAL)
    hProcess = procInfo.get('hProcess')
    if hProcess:
        win32event.WaitForSingleObject(hProcess, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(hProcess)
        sys.exit(rc)
    else:
        sys.exit(1)

def invoke(command, admin=False):
    """运行命令行命令"""
    try:
        if admin:
            # 以管理员权限运行 cmd.exe 并执行 command
            procInfo = shell.ShellExecuteEx(
                lpVerb='runas',
                lpFile='cmd.exe',
                lpParameters=f'/c {command}',
                nShow=win32con.SW_HIDE  # 隐藏黑窗，或者用 SW_SHOWNORMAL 显示
            )
            hProcess = procInfo.get('hProcess')
            if hProcess:
                win32event.WaitForSingleObject(hProcess, win32event.INFINITE)
                rc = win32process.GetExitCodeProcess(hProcess)
                return rc  # 返回退出码（0通常代表成功）
            else:
                raise RuntimeError("Failed to get process handle for admin command")
        else:
            result = subprocess.run(command, shell=True, check=True, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command '{command}' failed: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        raise RuntimeError(f"Failed to execute '{command}': {e}")

def call_url(url):
    """调用url"""
    try:
        # 使用start命令打开url
        subprocess.run(f'start "" "{url}"', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to open URL '{url}': {e.stderr.decode('utf-8')}")

dispatch = win32com.client.Dispatch

# 命令行操作
def create_cat(name):
    strategies_dir = Path("strategies")
    strategies_dir.mkdir(parents=True, exist_ok=True)
    file_path = strategies_dir / f"{name}.py"
    with file_path.open("wb") as fp:
        fp.write(f"""
# {name}.py
# 在这里输入你的描述
from util import Category, Item
from util import dispatch,invoke,unlink

{name}_cat = Category("{name}")
## 在这里注册你的Item
        """.encode('utf-8'))

# def add_new_cat_to_init_file(name):
    # init_file = Path("strategies") / "__init__.py"
    # init_file.parent.mkdir(parents=True, exist_ok=True)
    # if not init_file.exists():
    #     init_file.write_text("# strategies package\n", encoding='utf-8')
    # # 如果已经存在则不重复添加
    # init_text = init_file.read_text(encoding='utf-8')
    # import_line = f'    __import__("{name}", fromlist=["{name}"]).{name}_cat,\n'
    # if import_line.strip() in init_text:
    #     return
    # # 尝试在末尾的列表前插入，如果找不到则追加到文件末尾
    # # 假设 __all__ 或 CATS 列表存在于文件中，简单实现：在最后一行前插入，否则追加
    # lines = init_text.splitlines(keepends=True)
    # for i in range(len(lines)-1, -1, -1):
    #     if lines[i].strip().endswith(',') or lines[i].strip().endswith(']'):
    #         # 在此行之前插入新导入
    #         lines.insert(i+1, import_line)
    #         init_file.write_text(''.join(lines), encoding='utf-8')
    #         return
    # # 回退：追加
    # with init_file.open('a', encoding='utf-8') as f:
    #     f.write('\n' + import_line)

class InitFileModifier:
    def __init__(self, init_file_path: Path):
        self.init_file_path = init_file_path
        self.lines = []
        self.load()

    def load(self):
        if self.init_file_path.exists():
            with self.init_file_path.open('r', encoding='utf-8') as f:
                self.lines = f.readlines()
        else:
            self.lines = ["# strategies package\n"]

    def save(self):
        with self.init_file_path.open('w', encoding='utf-8') as f:
            f.writelines(self.lines)

    def add_import(self, name: str):
        import_line = f'    __import__("{name}", fromlist=["{name}"]).{name}_cat,\n'
        if any(import_line.strip() == line.strip() for line in self.lines):
            return  # Already exists

        # Find the last line that ends with ',' or ']'
        for i in range(len(self.lines) - 1, -1, -1):
            if self.lines[i].strip().endswith(',') or self.lines[i].strip().endswith(']'):
                self.lines.insert(i + 1, import_line)
                self.save()
                return

        # Fallback: append to the end
        self.lines.append('\n' + import_line)
        self.save()

def new_cat(name):
    create_cat(name)
    init_file = Path("strategies") / "__init__.py"
    init_modifier = InitFileModifier(init_file)
    init_modifier.add_import(name)

def main():
    parser = argparse.ArgumentParser(usage="util.py:帮助在项目中添加category")
    parser.add_argument("-new-cat", help="category name", dest="name")
    args = parser.parse_args()
    new_cat(args.name)

if __name__ == "__main__":
    main()