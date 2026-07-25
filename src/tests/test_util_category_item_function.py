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
    
    func = hello_world.strategies(0)
    assert func[0] == "输出hello world"
    assert func[1]() == True

def test_execute_strategy_in_item(given_cat):
    test_cat, hello_world = given_cat

    @hello_world.add_strategy("输出hello world")
    def hello_world_strategy():
        print("hello world")
        return True
    
    hello_world.use_strategy = 0
    assert hello_world.execute() == True