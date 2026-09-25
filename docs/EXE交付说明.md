# Windows EXE 交付说明

## 使用者如何打开

供组员测试的单文件位于仓库的[downloads/拓扑序设计器.exe](../downloads/拓扑序设计器.exe)。在 GitHub 打开文件页面后点击下载原始文件，保存到电脑任意目录，再双击运行；不需要安装 Python，也不需要保留附属文件夹。本地开发者重新构建的文件位于被 Git 忽略的`dist/拓扑序设计器.exe`。程序内“帮助 → 使用说明”可以查看操作步骤，“载入示例”包含任务书图1和已核实的部分培养方案关系。

本次测试版 SHA-256：`8FEDDA4FE68A6E21017613C75FFD99E9DA06176F19CDEBFB12E8D7A2E2B700CC`。若下载后打不开，可先核对文件是否完整，再把系统版本、报错截图和操作步骤发给技术负责人。

单文件版每次启动时要先释放内置的 Qt 和绘图库文件，因此打开速度会比源码版或目录版慢一些。解包阶段可能先等待片刻，随后显示应用启动画面。

## 开发者如何重新构建

在项目根目录使用 Python 3.12：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe scripts\create_app_icon.py
.\.venv\Scripts\python.exe scripts\build_exe.py --replace
```

首次构建且`dist/拓扑序设计器.exe`不存在时，可省略`--replace`。构建中间目录被Git忽略。

## 已验证范围

- 在 Windows 11 上完成单文件构建，并从项目外工作目录启动 EXE。
- 启动时不依赖项目源码路径或`PYTHONPATH`，主窗口能够显示并正常退出。
- 已将 Qt 所需的系统 ICU 与构建环境中同名但不兼容的 DLL 区分，避免`QtCore`加载失败。
- 使用说明、测试示例和图标均包含在 EXE 中。
- 当前 EXE 约 76.3 MB；本机普通图形界面启动抽测主窗口约 16.5 秒就绪。其他电脑可能不同。

本机已验证可用，但尚未证明其他电脑也能正常运行。请测试人员在另一台没有安装本项目 Python 环境的 Windows 10/11 电脑上人工验收，包括导入、分析、图导出和结果导出。
