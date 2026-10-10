import threading
from unittest.mock import patch

import pytest

from util import Category, Item


@pytest.fixture(scope="function")
def item_and_calls():
    item = Item(category=Category("test"), name="test item")
    item.checked.set(True)
    calls = []

    @item.add_strategy("test strategy")
    def strategy():
        calls.append("executed")

    return item, calls


def test_pause_then_continue_runs_strategy(item_and_calls):
    item, calls = item_and_calls
    item._pause_requested = True

    waiting = threading.Event()
    release_wait = threading.Event()

    def controlled_sleep(_seconds):
        waiting.set()
        release_wait.wait(timeout=2)

    with patch("util.time.sleep", controlled_sleep):
        worker = threading.Thread(target=item.execute)
        worker.start()

        assert waiting.wait(timeout=1)
        assert calls == []

        # 清除暂停标志，相当于继续执行。
        item._pause_requested = False
        release_wait.set()
        worker.join(timeout=2)

    assert not worker.is_alive()
    assert calls == ["executed"]


def test_kill_while_paused_skips_strategy(item_and_calls):
    item, calls = item_and_calls
    item._pause_requested = True

    waiting = threading.Event()
    release_wait = threading.Event()

    def controlled_sleep(_seconds):
        waiting.set()
        release_wait.wait(timeout=2)

    with patch("util.time.sleep", controlled_sleep):
        worker = threading.Thread(target=item.execute)
        worker.start()

        assert waiting.wait(timeout=1)
        item._kill_requested = True
        release_wait.set()
        worker.join(timeout=2)

    assert not worker.is_alive()
    assert calls == []


def test_kill_before_start_skips_strategy(item_and_calls):
    item, calls = item_and_calls
    item._kill_requested = True

    item.execute()

    assert calls == []