import sys
import types

win32com = types.ModuleType("win32com")
win32com_client = types.ModuleType("win32com.client")
win32com_client.Dispatch = lambda *args, **kwargs: None
win32com_client_gencache = types.ModuleType("win32com.client.gencache")
win32com_client.gencache = win32com_client_gencache
win32com_shell = types.ModuleType("win32com.shell")
win32com_shell_shell = types.ModuleType("win32com.shell.shell")
win32com_shell_shell.IsUserAnAdmin = lambda: False
win32com_shell.shell = win32com_shell_shell
win32com.client = win32com_client
win32com.shell = win32com_shell
sys.modules["win32com"] = win32com
sys.modules["win32com.client"] = win32com_client
sys.modules["win32com.client.gencache"] = win32com_client_gencache
sys.modules["win32com.shell"] = win32com_shell
sys.modules["win32com.shell.shell"] = win32com_shell_shell

win32event = types.ModuleType("win32event")
win32event.WaitForSingleObject = lambda *args, **kwargs: None
win32process = types.ModuleType("win32process")
win32process.GetExitCodeProcess = lambda *args, **kwargs: 0
win32con = types.ModuleType("win32con")
win32con.SW_HIDE = 0
win32con.SW_SHOWNORMAL = 1
sys.modules["win32event"] = win32event
sys.modules["win32process"] = win32process
sys.modules["win32con"] = win32con

from util import Category,Item
from util import dispatch,invoke,unlink
from viewmodels import RunViewModel
import pytest

@pytest.fixture
def given_cat():
    test_cat = Category("测试")

    hello_world = Item(test_cat,"hello world")
    return test_cat, hello_world

def test_add_strategy_in_item(given_cat):
    test_cat, hello_world = given_cat

    @hello_world.add_strategy("输出hello world")
    def hello_world_strategy():
        print("hello world")
        return True
    
    # hello_world.use_strategy = 0
    # hello_world.execute()
    assert len(hello_world.strategies) == 1

def test_get_strategy_in_item(given_cat):
    test_cat, hello_world = given_cat

    @hello_world.add_strategy("输出hello world")
    def hello_world_strategy():
        print("hello world")
        return True
    
    func = hello_world.strategies[0]
    assert func[0] == "输出hello world"
    assert func[1]() == True

def test_execute_strategy_in_item(given_cat):
    test_cat, hello_world = given_cat

    @hello_world.add_strategy("输出hello world")
    def hello_world_strategy():
        print("hello world")
        return True
    
    hello_world.use_strategy = 0
    assert hello_world.execute() == None


def test_runviewmodel_resume_paused_items():
    category = Category("测试")
    item = Item(category, "hello")
    item._pause_requested = True

    viewmodel = RunViewModel([item])
    viewmodel.resume()

    assert item._pause_requested is False

    viewmodel.continue_()
    assert item._pause_requested is False
