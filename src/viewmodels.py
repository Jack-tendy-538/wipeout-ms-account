# viewmodels.py
from typing import List
from util import Category, Item

class ChooseViewModel:
    """管理类别和条目的选择状态、策略选择，以及相关同步逻辑。"""
    def __init__(self, categories: List[Category]):
        self.categories = categories

    def toggle_item(self, item: Item) -> None:
        """当某个条目复选框变化时，同步其所属类别的全选状态。"""
        category = item.category
        all_checked = all(it.checked.get() for it in category.items)
        category.checked.set(all_checked)

    def toggle_category(self, category: Category) -> None:
        """当类别复选框变化时，同步其下所有条目的选中状态。"""
        checked = category.checked.get()
        for item in category.items:
            item.checked.set(checked)

    def set_item_strategy(self, item: Item, strategy_name: str) -> None:
        """为指定条目设置选中的策略名称，并更新对应的可执行函数。"""
        item.selected_strategy = strategy_name
        item.selected_strategy_fn = None
        for idx, (name, fn) in enumerate(item.strategies):
            if name == strategy_name:
                item.selected_strategy_fn = fn
                item.use_strategy = idx
                break

    def select_all(self) -> None:
        """全选所有条目。"""
        for category in self.categories:
            category.checked.set(True)
            for item in category.items:
                item.checked.set(True)

    def get_selected_items(self) -> List[Item]:
        """返回所有被选中的条目列表。"""
        return [
            item
            for category in self.categories
            for item in category.items
            if item.checked.get()
        ]