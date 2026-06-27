cats = [
    __import__("dev_logout", fromlist=["dev_logout"]).dev_cat,
    __import__("windows_logout", fromlist=["windows_logout"]).win_cat,
]