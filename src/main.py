# main.py
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import tkinter
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import sv_ttk

from strategies import cats
import util, text

if not util.is_admin():
    util.restart_as_admin()

util.high_dpi_make()

class UserAgreementWindow:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("User Agreement")
        sv_ttk.set_theme("light")
        self.render()

    def render(self):
        agreement_text = text.agreement_text
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        self.text_widget = tkinter.Text(self.frame, wrap=tkinter.WORD, height=15, width=60)
        self.text_widget.insert(tkinter.END, agreement_text)
        self.text_widget.pack(padx=20, pady=20)

        self.agreed_var = tkinter.BooleanVar(value=False)
        self.agreed_checkbox = ttk.Checkbutton(self.root, text=text.agree_check, variable=self.agreed_var)
        self.agreed_checkbox.pack(pady=10)
        self.ok_button = ttk.Button(self.root, text="OK", command=self.on_ok)
        self.ok_button.pack(pady=10)

    def on_ok(self):
        if self.agreed_var.get():
            self.root.destroy()
            main_window = ChooseWindow()
            main_window.root.mainloop()
        else:
            messagebox.showwarning("Agreement Required", text.agreement_warning)

class ChooseWindow:
    @dataclass
    class ItemFrame:
        obj: util.Item
        root: ttk.Frame
        category: Optional["util.Category"] = None

        def on_item_toggle(self):
            self.obj.toggle()
            if self.category is not None:
                all_checked = all(item.checked.get() for item in self.category.items)
                self.category.checked.set(all_checked)

        def on_strategy_selected(self, event: tkinter.Event):
            selected = self.strategy_var.get()
            self.set_selected_strategy(selected)

        def set_selected_strategy(self, strategy_name: str):
            self.obj.selected_strategy = strategy_name
            self.obj.selected_strategy_fn = None
            for idx, (name, fn) in enumerate(self.obj.strategies):
                if name == strategy_name:
                    self.obj.selected_strategy_fn = fn
                    self.obj.use_strategy = idx   # 添加这一行
                    break

        def sync_selected_strategy(self):
            self.set_selected_strategy(self.strategy_var.get())

        def render(self):
            self.frame = ttk.Frame(self.root, padding=5)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            self.strategies = [s[0] for s in self.obj.strategies]
            # 水平单行排列以下元素：选框（checkbox）、图标（image来自obj.icon）、标签（label显示obj.name）、下拉框（combobox选择strategy）以及可能有的链接
            ttk.Checkbutton(self.frame, text="", variable=self.obj.checked, command=self.on_item_toggle).pack(side=tkinter.LEFT)
            if self.obj.icon:
                ttk.Label(self.frame, image=tkinter.PhotoImage(file=util.download_icon(self.obj.icon))).pack(side=tkinter.LEFT, padx=5)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)
            self.strategy_var = tkinter.StringVar(value=self.strategies[0] if self.strategies else "")
            if self.strategies:
                self.set_selected_strategy(self.strategies[0])
            self.strategy_combobox = ttk.Combobox(self.frame, values=self.strategies, state="readonly", textvariable=self.strategy_var)
            self.strategy_combobox.bind("<<ComboboxSelected>>", self.on_strategy_selected)
            self.strategy_combobox.pack(side=tkinter.LEFT, padx=5)
            self.strategy_var.trace_add("write", lambda *args: self.sync_selected_strategy())
            for link_name, link_url in self.obj.links.items():
                link_label = ttk.Label(self.frame, text=link_name, foreground="blue", cursor="hand2")
                link_label.pack(side=tkinter.LEFT, padx=5)
                link_label.bind("<Button-1>", lambda e, url=link_url: util.open_link(url))
    @dataclass
    class CategoryFrame:
        obj: util.Category
        root: ttk.Frame
        item_frames: List["ChooseWindow.ItemFrame"] = field(default_factory=list, repr=False)

        def on_category_toggle(self):
            checked = self.obj.checked.get()
            for item in self.obj.items:
                item.checked.set(checked)

        def render(self):
            self.item_frames = []
            self.frame = ttk.LabelFrame(self.root, text=self.obj.name, padding=10)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            ttk.Checkbutton(self.frame, text="", variable=self.obj.checked, command=self.on_category_toggle).pack(side=tkinter.LEFT)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)
            for item in self.obj.items:
                item_frame = ChooseWindow.ItemFrame(item, self.frame, category=self.obj)
                item_frame.render()
                self.item_frames.append(item_frame)

        def sync_selected_strategies(self):
            for item_frame in self.item_frames:
                item_frame.sync_selected_strategy()
    @dataclass
    class MainFrame:
        root: tkinter.Tk
        categories: List[util.Category]
        category_frames: List["ChooseWindow.CategoryFrame"] = field(default_factory=list, repr=False)
        def render(self):
            self.category_frames = []
            self.frame = ttk.Frame(self.root, padding=10)
            self.frame.pack(fill=tkinter.BOTH, expand=True)
            for category in self.categories:
                category_frame = ChooseWindow.CategoryFrame(category, self.frame)
                category_frame.render()
                self.category_frames.append(category_frame)

        def sync_selected_strategies(self):
            for category_frame in self.category_frames:
                category_frame.sync_selected_strategies()

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Choose Items")
        sv_ttk.set_theme("light")
        ttk.Label(self.root, text=text.head).pack(pady=10)
        self.main_frame = ChooseWindow.MainFrame(self.root, cats)
        self.main_frame.render()

        self.info_panel = ttk.Frame(self.root, padding=10)
        # with 1 as _:
        ttk.Label(self.info_panel, text=text.panel).pack(anchor=tkinter.W)
        ttk.Button(self.info_panel, text=text.panel_issue, command=lambda: util.open_link("https://github.com/Jack-tendy-538/wipeout-ms-account/issues")).pack(anchor=tkinter.W, pady=5)
        ttk.Label(self.info_panel, text=text.panel_contrib).pack(anchor=tkinter.W)
        ttk.Button(self.info_panel, text=text.panel_issue, command=lambda: util.open_link("https://github.com/Jack-tendy-538/wipeout-ms-account/fork")).pack(anchor=tkinter.W, pady=5)

        ttk.Button(self.root, text=text.run, command=self.on_run).pack(pady=10)

    def on_run(self):
        self.main_frame.sync_selected_strategies()
        self.run()

    def run(self):
        selected_items = []
        for category in self.main_frame.categories:
            for item in category.items:
                if item.checked.get():
                    selected_items.append(item)
        if not selected_items:
            messagebox.showwarning("No Items Selected", text.run_warning)
            return
        self.root.destroy()
        run_window = RunWindow(selected_items)
        run_window.root.mainloop()

class RunWindow:
    def __init__(self, items: List[util.Item]):
        self.log = []
        self.items = items
        self.root = tkinter.Tk()
        self.root.title("Run Items")
        sv_ttk.set_theme("light")
        self.render()

    def render(self):
        self.root.geometry("400x260")
        
        self.frame = ttk.Frame(self.root, padding=10)
        ttk.Label(self.frame, text=text.motto).pack(pady=10)

        self.log_text = tkinter.Text(self.frame, height=8, wrap=tkinter.WORD, state=tkinter.DISABLED)
        self.log_text.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=(0,10))

        self.progress = ttk.Progressbar(self.frame, mode="indeterminate")
        self.progress.pack(fill=tkinter.X, padx=10, pady=5)
        self.progress.start()
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        self.root.after(100, self.run_items)

    def append_log(self, message: str):
        self.log.append(message)
        self.log_text.config(state=tkinter.NORMAL)
        self.log_text.insert(tkinter.END, message + "\n")
        self.log_text.see(tkinter.END)
        self.log_text.config(state=tkinter.DISABLED)
        self.root.update_idletasks()

    def run_items(self):
        for item in self.items:
            self.append_log(f"正在进行:{item.name}使用的策略:{item.selected_strategy}")
            item.execute()
            if item.is_error:
                self.append_log(f"{item.name}失败。错误信息: {item.error_message}")
            else:
                self.append_log(f"{item.name}完成。")
        self.progress.stop()
        messagebox.showinfo("Run Complete", text.finish)
        self.root.destroy()

def main():
    agreement_window = UserAgreementWindow()
    agreement_window.root.mainloop()

if __name__ == "__main__":
    main()