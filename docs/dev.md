# wipeout-ms-account开发者文档
## :link: 常用链接
<!--水平排列以下元素-->
<table align="center">
  <tr>
    <td align="center"><a href="https://blog.csdn.net/A_art_xiang/article/details/134404369"><img src="https://img.shields.io/badge/pywin32-文档-blue?logo=python" alt="pywin32文档"></a></td>
    <td align="center"><a href="https://learn.microsoft.com/zh-cn/windows/apps/windows-sdk/downloads"><img src="https://img.shields.io/badge/Windows-SDK-blue?logo=windows" alt="Windows SDK"></a></td>
    <td align="center"><a href="https://github.com/Jack-tendy-538/wipeout-ms-account/edit/main/docs/dev.md"><img src="https://img.shields.io/badge/修改-此页-orange?logo=github" alt="修改此页"></a></td>
  </tr>
</table>

> 我们欢迎你参与开发此页！

## :thinking: 如何开始
<details>
<summary>搭建虚拟环境并安装依赖</summary>

```bash
# 创建虚拟环境
python -m venv woma
# 激活虚拟环境
# 此脚本只能在Windows上运行
woma\Scripts\activate
pip install -r requirements.txt
```

</details>
<details>
<summary>使用new-cat命令套用模板</summary>

你可以使用`new-cat`命令来创建一个新的分类目录，并套用指定的模板，像这样，在cmd窗口输入下面的命令，而pwsh窗口则使用`.\new-cat.ps1 <模板名>`。
```bash
new-cat <模板名>
```
现在你可以在src/strategies目录下找到一个新的py文件，像这样输入代码：
```python

# hello.py
# 在这里输入你的描述
from util import Category, Item
from util import dispatch,invoke,unlink
import tkinter.messagebox as ms
hello_cat = Category("hello")
## 在这里注册你的Item
        
destory = Item(hello_cat,"从微软手中夺回话语权")
@destory.add_strategy("强力删除Windows文件夹")
def demand():
    invoke("echo 你已被微软封禁，无法使用本软件！;pause")
    ms.showwarning("Warnings","窗户防御者(Windows Defender)认为此软件十分可疑。\n我们将装载微软大战代码!")
    
```
效果如图：

![选择界面](https://forum.smart-teach.cn/assets/files/2026-07-11/1783763130-577124-image.png)

![执行界面](https://forum.smart-teach.cn/assets/files/2026-07-11/1783763148-964898-image.png)

~~确实有点猎奇~~

</details>

## :toolbox: util函数

下表列出了util可调用的函数和类，供开发者参考。

| 名称 | 形参 | 返回值 | 说明 |
| --- | --- | --- | --- |
| Category | name: str | Category对象 | 用于创建一个新的分类目录 |
| Item | category: Category, name: str | Item对象 | 用于创建一个新的Item |
| invoke | command: str | None | 用于执行一个命令 |
| dispatch | command: str | None | 用于调度一个命令 |
| unlink | path: str | None | 用于删除一个文件或目录 |
| call_url | url: str | None | 用于打开一个URL |

# :heart: 感谢你的支持!
