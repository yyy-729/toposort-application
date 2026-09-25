"""无控制台启动入口；启动失败时显示消息并保留错误日志。"""

from __future__ import annotations

import ctypes
import os
import sys
import traceback
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    sys.path.insert(0, str(project_root / "src"))
    try:
        from toposort_app.main import main as start_application

        start_application()
    except Exception:
        log_path = project_root / "artifacts" / "startup_error.log"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(traceback.format_exc(), encoding="utf-8")
            message = f"应用启动失败。请检查错误日志：\n{log_path}"
        except OSError:
            message = "应用启动失败。请运行 scripts\\run_app.bat 查看详细错误。"
        ctypes.windll.user32.MessageBoxW(None, message, "拓扑序设计器", 0x10)


if __name__ == "__main__":
    main()
