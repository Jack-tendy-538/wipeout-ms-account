import threading
import unittest
from unittest.mock import patch

from util import Category, Item


class TestItemStrategyPauseKillContinue(unittest.TestCase):
    def create_item(self):
        item = Item(category=Category("test"), name="test item")
        item.checked.set(True)
        calls = []

        @item.add_strategy("test strategy")
        def strategy():
            calls.append("executed")

        return item, calls

    def test_pause_then_continue_runs_strategy(self):
        item, calls = self.create_item()
        item._pause_requested = True

        waiting = threading.Event()
        release_wait = threading.Event()

        def controlled_sleep(_seconds):
            waiting.set()
            release_wait.wait(timeout=2)

        with patch("util.time.sleep", controlled_sleep):
            worker = threading.Thread(target=item.execute)
            worker.start()

            self.assertTrue(waiting.wait(timeout=1))
            self.assertEqual(calls, [])

            # 清除暂停标志，相当于继续执行。
            item._pause_requested = False
            release_wait.set()
            worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        self.assertEqual(calls, ["executed"])

    def test_kill_while_paused_skips_strategy(self):
        item, calls = self.create_item()
        item._pause_requested = True

        waiting = threading.Event()
        release_wait = threading.Event()

        def controlled_sleep(_seconds):
            waiting.set()
            release_wait.wait(timeout=2)

        with patch("util.time.sleep", controlled_sleep):
            worker = threading.Thread(target=item.execute)
            worker.start()

            self.assertTrue(waiting.wait(timeout=1))
            item._kill_requested = True
            release_wait.set()
            worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        self.assertEqual(calls, [])

    def test_kill_before_start_skips_strategy(self):
        item, calls = self.create_item()
        item._kill_requested = True

        item.execute()

        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()