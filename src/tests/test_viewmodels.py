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


def test_set_item_checked_updates_category_state():
    category = Category("test")
    first = Item(category=category, name="first")
    second = Item(category=category, name="second")
    viewmodel = ChooseViewModel([category])

    viewmodel.set_item_checked(first, True)
    assert first.checked.get() is True
    assert category.checked.get() is False

    viewmodel.set_item_checked(second, True)
    assert category.checked.get() is True

    viewmodel.set_item_checked(first, False)
    assert first.checked.get() is False
    assert category.checked.get() is False


def test_set_category_checked_updates_all_items():
    category = Category("test")
    first = Item(category=category, name="first")
    second = Item(category=category, name="second")
    viewmodel = ChooseViewModel([category])

    viewmodel.set_category_checked(category, True)
    assert first.checked.get() is True
    assert second.checked.get() is True

    viewmodel.set_category_checked(category, False)
    assert first.checked.get() is False
    assert second.checked.get() is False


def test_get_selected_items_tracks_direct_updates():
    category = Category("test")
    first = Item(category=category, name="first")
    second = Item(category=category, name="second")
    viewmodel = ChooseViewModel([category])

    viewmodel.set_item_checked(first, True)
    assert viewmodel.get_selected_items() == [first]
