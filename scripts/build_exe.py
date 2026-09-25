"""构建无需 Python 环境的 Windows 单文件 EXE。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="构建拓扑序设计器 Windows EXE")
    parser.add_argument("--replace", action="store_true", help="替换已有的生成 EXE")
    args = parser.parse_args()

    if sys.version_info[:2] != (3, 12):
        parser.error("必须使用 Python 3.12 构建")

    project_root = Path(__file__).resolve().parents[1]
    dist_root = (project_root / "dist").resolve()
    executable = project_root / "dist" / "拓扑序设计器.exe"
    if executable.exists():
        if not executable.resolve().is_relative_to(dist_root) or not args.replace:
            parser.error("生成 EXE 已存在；确认后使用 --replace 重新构建")
        if not executable.is_file():
            parser.error("现有目标不是文件，拒绝覆盖")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--distpath",
        str(dist_root),
        "--workpath",
        str(project_root / "build" / "pyinstaller"),
    ]
    if args.replace:
        command.append("--noconfirm")
    command.append(str(project_root / "scripts" / "toposort_app.spec"))
    subprocess.run(command, cwd=project_root, check=True)

    if not executable.is_file():
        parser.error(f"未找到构建结果：{executable}")

    print(f"单文件 EXE：{executable}")
    print(f"文件大小：{executable.stat().st_size / (1024 * 1024):.1f} MB")
    print("可以单独复制该 EXE 到其他 Windows 电脑运行。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
