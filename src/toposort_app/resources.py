"""定位源码运行和 PyInstaller 打包运行所需的资源。"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """优先读取 EXE 同目录的外部文件，再读取打包内资源。"""
    if getattr(sys, "frozen", False):
        executable_root = Path(sys.executable).resolve().parent
        external = executable_root / relative_path
        if external.exists():
            return external
        bundle_root = Path(getattr(sys, "_MEIPASS", executable_root))
        return bundle_root / relative_path
    return Path(__file__).resolve().parents[2] / relative_path
