'''
在工作流中解析提交修改的文件路径，并将其转换为适合在工作流中使用的格式。
'''
import sys,re,json
from pathlib import Path
if len(sys.argv) < 2:
    print("请提供提交修改的文件路径作为参数。")
    sys.exit(1)

file_paths = Path(sys.argv[1])

# 平替 jq 命令，将文件路径转换为 JSON 数组
files = [path for path in file_paths.read_text().split('\n') if path]

# 输出到 GitHub Output
print(json.dumps(files))
