from util import Category,Item
from util import dispatch,invoke,unlink
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
    
    hello_world.checked.set(True)
    hello_world.use_strategy = 0
    assert hello_world.execute() == True


def test_select_strategy_by_name_updates_runtime_state(given_cat):
    test_cat, hello_world = given_cat

    @hello_world.add_strategy("输出hello world")
    def hello_world_strategy():
        return "hello"

    @hello_world.add_strategy("输出bye")
    def hello_world_strategy_bye():
        return "bye"

    hello_world.set_selected_strategy("输出bye")
    assert hello_world.selected_strategy == "输出bye"
    assert hello_world.use_strategy == 1
    assert hello_world.selected_strategy_fn is not None

    hello_world.checked.set(True)
    assert hello_world.execute() == "bye"
