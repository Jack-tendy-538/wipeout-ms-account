# main.py
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import tkinter
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import sv_ttk

from strategies import cats
import util, text
from viewmodels import ChooseViewModel
import time

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

# main.py 中的 ChooseWindow 部分（含嵌套类）
# 需确保已导入：tkinter, ttk, sv_ttk, util, text, ChooseViewModel

class ChooseWindow:
    @dataclass
    class ItemFrame:
        obj: util.Item
        root: ttk.Frame
        viewmodel: "ChooseViewModel"          # 传入 ViewModel
        category: Optional["util.Category"] = None

        def on_item_toggle(self):
            # 调用 ViewModel 同步类别全选状态
            self.viewmodel.toggle_item(self.obj)

        def on_strategy_selected(self, event: tkinter.Event):
            selected = self.strategy_var.get()
            self.viewmodel.set_item_strategy(self.obj, selected)

        def sync_selected_strategy(self):
            # 将当前下拉框的值同步到条目对象
            self.viewmodel.set_item_strategy(self.obj, self.strategy_var.get())

        def render(self):
            self.frame = ttk.Frame(self.root, padding=5)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            self.strategies = [s[0] for s in self.obj.strategies]
            btn_state = "normal" if getattr(self.obj, "allowed", True) else "disabled"
            ttk.Checkbutton(
                self.frame, text="", variable=self.obj.checked,
                command=self.on_item_toggle, state=btn_state
            ).pack(side=tkinter.LEFT)
            if self.obj.icon:
                self.icon_image = tkinter.PhotoImage(file=self.obj.icon)
                ttk.Label(self.frame, image=self.icon_image).pack(side=tkinter.LEFT, padx=5)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)

            self.strategy_var = tkinter.StringVar(value=self.strategies[0] if self.strategies else "")
            if self.strategies:
                # 设置默认策略
                self.viewmodel.set_item_strategy(self.obj, self.strategies[0])
            self.strategy_combobox = ttk.Combobox(
                self.frame, values=self.strategies, state="readonly",
                textvariable=self.strategy_var
            )
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
        viewmodel: "ChooseViewModel"          # 传入 ViewModel
        item_frames: List["ChooseWindow.ItemFrame"] = field(default_factory=list)

        def on_category_toggle(self):
            self.viewmodel.toggle_category(self.obj)

        def render(self):
            self.item_frames = []
            self.frame = ttk.LabelFrame(self.root, text=self.obj.name, padding=10)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            ttk.Checkbutton(
                self.frame, text="", variable=self.obj.checked,
                command=self.on_category_toggle
            ).pack(side=tkinter.LEFT)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)
            for item in self.obj.items:
                item_frame = ChooseWindow.ItemFrame(
                    item, self.frame, viewmodel=self.viewmodel, category=self.obj
                )
                item_frame.render()
                self.item_frames.append(item_frame)

        def sync_selected_strategies(self):
            for item_frame in self.item_frames:
                item_frame.sync_selected_strategy()

    @dataclass
    class MainFrame:
        root: tkinter.Tk
        categories: List[util.Category]
        viewmodel: "ChooseViewModel"          # 传入 ViewModel
        category_frames: List["ChooseWindow.CategoryFrame"] = field(default_factory=list)

        def render(self):
            self.category_frames = []
            self.frame = ttk.Frame(self.root, padding=10)
            self.frame.pack(fill=tkinter.BOTH, expand=True)
            for category in self.categories:
                category_frame = ChooseWindow.CategoryFrame(
                    category, self.frame, viewmodel=self.viewmodel
                )
                category_frame.render()
                self.category_frames.append(category_frame)

        def sync_selected_strategies(self):
            for category_frame in self.category_frames:
                category_frame.sync_selected_strategies()

    @dataclass
    class MainMenu:
        root:tkinter.Tk
        def render(self):
            self.menubar = tkinter.Menu(self.root)
            self.root.config(menu=self.menubar)
            self.file_menu = tkinter.Menu(self.menubar, tearoff=0)
            self.file_menu.add_command(label=text.menu_exit, command=self.root.quit)
            self.menubar.add_cascade(label=text.menu_file, menu=self.file_menu)
            self.select_menu = tkinter.Menu(self.menubar, tearoff=0)
            self.select_menu.add_command(label=text.menu_select_all, command=ChooseViewModel.select_all)
            self.select_menu.add_cascade(label=text.menu_select_category, menu=self.select_menu)
    
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("选择窗口")
        sv_ttk.set_theme("light")
        ttk.Label(self.root, text=text.head).pack(pady=10)

        # 创建 ViewModel 并传递给 UI 框架
        self.viewmodel = ChooseViewModel(cats)
        self.main_frame = ChooseWindow.MainFrame(
            self.root, cats, viewmodel=self.viewmodel
        )
        self.main_frame.render()

        self.info_panel = ttk.Frame(self.root, padding=10)
        ttk.Label(self.info_panel, text=text.panel).pack(anchor=tkinter.W)
        ttk.Button(
            self.info_panel, text=text.panel_issue,
            command=lambda: util.open_link("https://github.com/Jack-tendy-538/wipeout-ms-account/issues")
        ).pack(anchor=tkinter.W, pady=5)
        ttk.Label(self.info_panel, text=text.panel_contrib).pack(anchor=tkinter.W)
        ttk.Button(
            self.info_panel, text=text.panel_issue,
            command=lambda: util.open_link("https://github.com/Jack-tendy-538/wipeout-ms-account/fork")
        ).pack(anchor=tkinter.W, pady=5)

        ttk.Button(self.root, text="全选策略", command=self.choose_all_items).pack(pady=10)
        ttk.Button(self.root, text=text.run, command=self.on_run).pack(pady=10)

    def on_run(self):
        self.main_frame.sync_selected_strategies()
        self.run()

    def choose_all_items(self):
        self.viewmodel.select_all()
        # 同步 UI 中的策略选择（全选不改变策略，但确保所有条目的策略下拉框显示正确）
        self.main_frame.sync_selected_strategies()

    def run(self):
        selected_items = self.viewmodel.get_selected_items()
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
        # control flags manipulated by pause/kill methods
        for it in self.items:
            setattr(it, "_pause_requested", False)
            setattr(it, "_kill_requested", False)
        self.root = tkinter.Tk()
        self.root.title("Run Items")
        sv_ttk.set_theme("light")
        self.render()

    def pause(self):
        """Pause any strategies that have not yet started for all remaining items."""
        for it in self.items:
            # only affect strategies that haven't started
            it._pause_requested = True

    def kill(self):
        """Kill (skip) any strategies that have not yet started for all remaining items."""
        for it in self.items:
            it._kill_requested = True
            # un-pause so wrappers can detect kill and exit promptly
            it._pause_requested = False

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