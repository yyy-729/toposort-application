# 拓扑序设计器

“高级算法原理实践”本地桌面应用。程序使用 Python 3.12 和 PySide6 开发，能够输入或导入有向关系、绘制关系图、枚举多种拓扑排序、检测环并导出结果。

当前完整应用版本：`2.0.0`

![应用界面预览](docs/images/应用界面预览.png)

## 主要功能

- 图形界面输入 `<前驱节点,后继节点>` 关系
- 从 UTF-8 TXT 文件导入关系数据
- 分层显示有向关系图
- PNG、SVG、PDF 关系图导出
- 尽可能枚举全部拓扑排序结果
- 可配置结果数量上限，并明确标记是否完整枚举
- TXT 排序结果导出
- 自环和普通有向环检测，并高亮具体环路
- 中文逗号、括号错误、空节点、重复关系等异常提示
- 后台执行计算，避免界面在枚举时失去响应

## 运行环境

- Windows 10 或 Windows 11
- Python 3.12
- PySide6 6.11.2
- NetworkX 3.6.1
- Matplotlib 3.11.2

本机普通 `python` 可能指向其他版本，请统一使用 `py -3.12`。

## 最简单的运行方法

1. 安装 Python 3.12。
2. 双击 `安装依赖.bat`。
3. 双击 `启动应用.bat`。

也可以在 VS Code 的 PowerShell 终端执行：

```powershell
py -3.12 -m pip install -r requirements.txt
$env:PYTHONPATH=(Resolve-Path .\src).Path
py -3.12 -m toposort_app
```

程序启动后已经提供一组课程关系示例，点击“运行分析”即可看到关系图和多个拓扑排序结果。

## 输入格式

每行输入一个关系，必须使用西文尖括号和西文逗号：

```text
<程序设计基础,数据结构>
<离散数学,数据结构>
<数据结构,算法设计>
```

`<a,b>` 表示 a 必须在 b 之前。

## 命令行核心演示

图形界面之外，核心模块仍可独立运行：

```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
py -3.12 -m toposort_core examples\multiple.txt --limit 1000 --output results.txt
```

命令行退出状态：

- `0`：成功
- `2`：输入格式错误
- `3`：存在环
- `4`：文件读取或结果写入失败

## 技术二集成接口

```python
from toposort_core import solve_text

result = solve_text(input_text, max_results=1000)
```

界面使用 `result.errors`、`result.warnings`、`result.cycle`、`result.orders` 和 `result.is_complete` 显示对应状态，不需要修改核心模块内部代码。

## 项目检查

安装开发依赖：

```powershell
py -3.12 -m pip install -r requirements-dev.txt
```

运行检查：

```powershell
py -3.12 -m ruff check .
$env:QT_QPA_PLATFORM="offscreen"
py -3.12 -m pytest
```

生成界面预览图：

```powershell
$env:QT_QPA_PLATFORM="offscreen"
py -3.12 scripts\render_app_preview.py artifacts\app_preview.png
```

## 目录说明

- `src/toposort_core/`：关系解析、环检测、拓扑排序和结果导出
- `src/toposort_app/`：PySide6 图形界面和关系图显示
- `tests/`：核心、命令行和图形界面自动化测试
- `examples/`：正常、多结果、有环和错误格式示例
- `docs/`：技术说明、测试清单和界面预览

