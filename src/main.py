# main.py
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import tkinter
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import sv_ttk

from strategies import cats
import util

class UserAgreementWindow:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("User Agreement")
        sv_ttk.set_theme("light")
        self.render()

    def render(self):
        agreement_text = (
            "Please read and accept the following user agreement before proceeding:\n\n"
            "1. You agree to use this software at your own risk.\n"
            "2. The developers are not responsible for any data loss or damage.\n"
            "3. You agree to comply with all applicable laws and regulations.\n"
            "4. This software is provided 'as-is' without any warranties.\n\n"
            "Do you accept the terms of this agreement?"
        )
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        self.text_widget = tkinter.Text(self.frame, wrap=tkinter.WORD, height=15, width=60)
        self.text_widget.insert(tkinter.END, agreement_text)
        self.text_widget.pack(padx=20, pady=20)

        self.agreed_var = tkinter.BooleanVar(value=False)
        self.agreed_checkbox = ttk.Checkbutton(self.root, text="I accept the terms of this agreement", variable=self.agreed_var)
        self.agreed_checkbox.pack(pady=10)
        self.ok_button = ttk.Button(self.root, text="OK", command=self.on_ok)
        self.ok_button.pack(pady=10)

    def on_ok(self):
        if self.agreed_var.get():
            self.root.destroy()
            main_window = ChooseWindow()
            main_window.root.mainloop()
        else:
            messagebox.showwarning("Agreement Required", "You must accept the user agreement to proceed.")

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

        def render(self):
            self.frame = ttk.Frame(self.root, padding=5)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            self.strategies = [s[0] for s in self.obj.strategies]
            # 水平单行排列以下元素：选框（checkbox）、图标（image来自obj.icon）、标签（label显示obj.name）、下拉框（combobox选择strategy）以及可能有的链接
            ttk.Checkbutton(self.frame, text="", variable=self.obj.checked, command=self.on_item_toggle).pack(side=tkinter.LEFT)
            if self.obj.icon:
                ttk.Label(self.frame, image=tkinter.PhotoImage(file=util.download_icon(self.obj.icon))).pack(side=tkinter.LEFT, padx=5)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)
            ttk.Combobox(self.frame, values=self.strategies, state="readonly").pack(side=tkinter.LEFT, padx=5)
            for link_name, link_url in self.obj.links.items():
                ttk.Label(self.frame, text=link_name, foreground="blue", cursor="hand2").pack(side=tkinter.LEFT, padx=5)
                self.frame.bind("<Button-1>", lambda e, url=link_url: util.open_link(url))
    @dataclass
    class CategoryFrame:
        obj: util.Category
        root: ttk.Frame

        def on_category_toggle(self):
            checked = self.obj.checked.get()
            for item in self.obj.items:
                item.checked.set(checked)

        def render(self):
            self.frame = ttk.LabelFrame(self.root, text=self.obj.name, padding=10)
            self.frame.pack(fill=tkinter.X, padx=10, pady=5)
            ttk.Checkbutton(self.frame, text="", variable=self.obj.checked, command=self.on_category_toggle).pack(side=tkinter.LEFT)
            ttk.Label(self.frame, text=self.obj.name).pack(side=tkinter.LEFT, padx=5)
            for item in self.obj.items:
                item_frame = ChooseWindow.ItemFrame(item, self.frame, category=self.obj)
                item_frame.render()
    @dataclass
    class MainFrame:
        root: tkinter.Tk
        categories: List[util.Category]
        def render(self):
            self.frame = ttk.Frame(self.root, padding=10)
            self.frame.pack(fill=tkinter.BOTH, expand=True)
            for category in self.categories:
                category_frame = ChooseWindow.CategoryFrame(category, self.frame)
                category_frame.render()
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Choose Items")
        sv_ttk.set_theme("light")
        ttk.Label(self.root, text="Please choose the items you want to use:").pack(pady=10)
        self.main_frame = ChooseWindow.MainFrame(self.root, cats)
        self.main_frame.render()
        ttk.Button(self.root, text="Run", command=self.on_run).pack(pady=10)

    def on_run(self):
        self.run()

    def run(self):
        selected_items = []
        for category in self.main_frame.categories:
            if category.checked.get():
                for item in category.items:
                    if item.checked.get():
                        selected_items.append(item)
        if not selected_items:
            messagebox.showwarning("No Items Selected", "Please select at least one item to run.")
            return
        self.root.destroy()
        run_window = RunWindow(selected_items)
        run_window.run()

class RunWindow:
    def __init__(self, items: List[util.Item]):
        self.items = items
        self.root = tkinter.Tk()
        self.root.title("Run Items")
        sv_ttk.set_theme("light")
        self.render()

    def render(self):
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        ttk.Label(self.frame, text="Running selected items...").pack(pady=10)
        self.progress = ttk.Progressbar(self.frame, mode="indeterminate")
        self.progress.pack(fill=tkinter.X, padx=10, pady=10)
        self.progress.start()
        self.root.after(100, self.run_items)

    def run_items(self):
        for item in self.items:
            item.execute()
        self.progress.stop()
        messagebox.showinfo("Run Complete", "All selected items have been executed.")

def main():
    agreement_window = UserAgreementWindow()
    agreement_window.root.mainloop()

if __name__ == "__main__":
    main()