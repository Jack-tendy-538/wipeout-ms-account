# util.py
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from shutil import rmtree, unlink
import win32com.client
import win32event
import win32process
import win32con
# import win32com.client.gencache as gencache
import win32com.shell.shell as shell
from typing import Any, Callable, Dict, List, Optional, Tuple

@dataclass
class Category:
    name: str
    items: List["Item"] = field(default_factory=list)
    errors: List[Tuple[str, str, str]] = field(default_factory=list)
    checked: bool = True

    def __repr__(self) -> str:
        return f"Category(name={self.name!r}, items={len(self.items)}, checked={self.checked})"

    def toggle(self) -> None:
        self.checked = not self.checked
        for item in self.items:
            item.checked = self.checked

    def add_item(self, item: "Item") -> "Item":
        self.items.append(item)
        return item

@dataclass
class Item:
    category: Category
    name: str
    links: Dict[str, str] = field(default_factory=dict)
    icon: Optional[str] = None
    checked: bool = True
    is_error: bool = False
    strategies: List[Tuple[str, Callable[..., Any]]] = field(default_factory=list)
    use_strategy: int = 0

    def __post_init__(self) -> None:
        self.category.add_item(self)

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, checked={self.checked}, strategies={len(self.strategies)})"

    def toggle(self) -> None:
        self.checked = not self.checked

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

# 实用函数

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

def invoke(command,admin=False):
	"""运行命令行命令"""
	try:
		if admin:
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
		else:
			result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			return result.stdout.decode('utf-8')
	except subprocess.CalledProcessError as e:
		raise RuntimeError(f"Command '{command}' failed with error: {e.stderr.decode('utf-8')}")

def call_url(url):
	"""调用url"""
	try:
		# 使用start命令打开url
		subprocess.run(f'start "" "{url}"', shell=True, check=True)
	except subprocess.CalledProcessError as e:
		raise RuntimeError(f"Failed to open URL '{url}': {e.stderr.decode('utf-8')}")

dispatch = win32com.client.Dispatch