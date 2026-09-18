# 拓扑排序核心模块

本目录是“高级算法原理实践”中技术一负责的核心功能。它提供关系解析、环检测、拓扑排序枚举、结果导出和命令行演示，不包含图形界面和关系图绘制。

当前交付版本：`1.0.0`

## 环境

- Python 3.12
- 运行时只使用 Python 标准库
- 开发检查使用 pytest、pytest-cov 和 Ruff

本机普通 `python` 可能指向其他 Python，请统一使用 `py -3.12`。

## 安装开发环境

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.12 -m pip install -e ".[dev]"
```

## 命令行演示

```powershell
py -3.12 -m toposort_core examples\multiple.txt --limit 1000 --output results.txt
```

如果暂时无法联网安装开发依赖，也可以直接从源码运行：

```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
py -3.12 -m toposort_core examples\multiple.txt --limit 1000 --output results.txt
py -3.12 -m unittest discover -s tests -v
```

退出状态：

- `0`：成功
- `2`：输入格式错误
- `3`：存在环
- `4`：文件读取或结果写入失败

## 提供给技术二的接口

```python
from toposort_core import export_result, solve_text

text = "<离散数学,数据结构>\n<数据结构,算法设计>"
result = solve_text(text, max_results=1000)

if result.errors:
    print(result.errors)
elif result.has_cycle:
    print(result.cycle)
else:
    print(result.orders)
    export_result("results.txt", result)
```

技术二只需要调用 `solve_text()` 获取结果，或调用 `export_result()` 导出结果，不需要修改核心模块内部代码。

也可以安装交付包中的 wheel：

```powershell
py -3.12 -m pip install toposort_core-1.0.0-py3-none-any.whl
```

## 检查

```powershell
py -3.12 -m ruff check .
py -3.12 -m pytest --cov=toposort_core --cov-fail-under=90
```
