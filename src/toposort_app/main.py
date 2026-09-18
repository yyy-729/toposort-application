"""桌面应用启动入口。"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import APP_STYLESHEET


def load_chinese_font() -> str:
    """显式加载 Windows 中文字体，兼容普通和无界面渲染。"""
    candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    )
    for path in candidates:
        if not path.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            return families[0]
    return "Sans Serif"


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setApplicationName("拓扑序设计器")
    app.setApplicationDisplayName("拓扑序设计器")
    app.setOrganizationName("高级算法原理实践项目组")
    app.setStyle("Fusion")
    app.setFont(QFont(load_chinese_font(), 10))
    app.setStyleSheet(APP_STYLESHEET)
    return app


def main(argv: Sequence[str] | None = None) -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = create_application(argv)
    window = MainWindow()
    window.show()

    auto_close = os.environ.get("TOPOSORT_AUTO_CLOSE_MS", "").strip()
    if auto_close:
        try:
            delay = max(1, int(auto_close))
        except ValueError:
            delay = 1000
        QTimer.singleShot(delay, window.close)

    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
