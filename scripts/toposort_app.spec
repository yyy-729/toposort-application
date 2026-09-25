# -*- mode: python ; coding: utf-8 -*-
"""Windows 桌面应用的可重复构建配置。"""

from pathlib import Path

project_root = Path(SPECPATH).resolve().parent
entry = project_root / "scripts" / "exe_entry.py"
icon = project_root / "assets" / "app.ico"

analysis = Analysis(
    [str(entry)],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[
        (str(project_root / "docs" / "使用说明.md"), "docs"),
        (str(project_root / "docs" / "images" / "培养方案阶段规划预览.png"), "docs/images"),
        (str(project_root / "docs" / "images" / "过程回放预览.png"), "docs/images"),
        (str(project_root / "examples"), "examples"),
        (str(icon), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff"],
    noarchive=False,
)
# 构建环境中的 Poppler 也带有 icuuc.dll，但 Qt6Core 需要 Windows 系统 ICU
# 提供的未加版本后缀的函数。误把 Poppler 的 DLL 放到应用根目录会导致
# “DLL load failed while importing QtCore: 找不到指定的程序”。
analysis.binaries = [
    item
    for item in analysis.binaries
    if Path(item[0]).name.lower() not in {"icuuc.dll", "icudt78.dll"}
]
archive = PYZ(analysis.pure)
application = EXE(
    archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="拓扑序设计器",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(icon),
)
