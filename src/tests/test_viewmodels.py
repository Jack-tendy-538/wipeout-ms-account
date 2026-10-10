import pytest

from util import Category, Item
from viewmodels import ChooseViewModel


def test_set_item_strategy_updates_strategy_and_index():
    item = Item(category=Category("test"), name="test item")
    strategies = [lambda: "first", lambda: "second"]
    item.strategies = [("first", strategies[0]), ("second", strategies[1])]
    viewmodel = ChooseViewModel([item.category])

    viewmodel.set_item_strategy(item, "second")

    assert item.selected_strategy == "second"
    assert item.selected_strategy_fn is strategies[1]
    assert item.use_strategy == 1


def test_set_item_strategy_rejects_unknown_name_without_changing_state():
    item = Item(category=Category("test"), name="test item")
    strategy = lambda: "first"
    item.strategies = [("first", strategy)]
    item.selected_strategy = "first"
    item.selected_strategy_fn = strategy
    item.use_strategy = 0
    viewmodel = ChooseViewModel([item.category])

    with pytest.raises(ValueError, match="Unknown strategy 'missing'"):
        viewmodel.set_item_strategy(item, "missing")

    assert item.selected_strategy == "first"
    assert item.selected_strategy_fn is strategy
    assert item.use_strategy == 0
