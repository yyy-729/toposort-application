"""桌面应用启动入口。"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen

from .resources import resource_path
from .theme import APP_STYLESHEET, make_palette


def load_chinese_font() -> str:
    """显式加载 Windows 中文字体，兼容普通和无界面渲染。"""
    if sys.platform == "win32" and os.environ.get("QT_QPA_PLATFORM") != "offscreen":
        return "Microsoft YaHei UI"
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
    icon_path = resource_path("assets/app.ico")
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setPalette(make_palette(False))
    app.setStyleSheet(APP_STYLESHEET)
    return app


def create_splash() -> QSplashScreen:
    """用轻量 Qt 画面反馈启动进度，随后再加载绘图库。"""
    pixmap = QPixmap(520, 234)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    background = QLinearGradient(0, 0, 520, 234)
    background.setColorAt(0, QColor("#152746"))
    background.setColorAt(1, QColor("#273B71"))
    painter.fillRect(pixmap.rect(), background)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#758AFF"))
    painter.drawRoundedRect(30, 36, 52, 52, 15, 15)
    painter.setPen(QColor("#FFFFFF"))
    painter.setFont(QFont("Microsoft YaHei UI", 22, QFont.Weight.Bold))
    painter.drawText(41, 72, "拓")
    painter.setFont(QFont("Microsoft YaHei UI", 19, QFont.Weight.Bold))
    painter.drawText(102, 67, "拓扑序设计器")
    painter.setFont(QFont("Microsoft YaHei UI", 10))
    painter.setPen(QColor("#BECBE7"))
    painter.drawText(103, 87, "TOPOLOGICAL SORT WORKSPACE")
    painter.setBrush(QColor("#6278DE"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(30, 179, 460, 4, 2, 2)
    painter.setBrush(QColor("#B6C5FF"))
    painter.drawRoundedRect(30, 179, 140, 4, 2, 2)
    painter.setPen(QColor("#D7E0F7"))
    painter.setFont(QFont("Microsoft YaHei UI", 10))
    painter.drawText(30, 211, "正在准备关系图与算法模块…")
    painter.end()
    return QSplashScreen(pixmap)


def main(argv: Sequence[str] | None = None) -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = create_application(argv)
    app.setQuitOnLastWindowClosed(False)
    splash = create_splash()
    splash.show()
    app.processEvents()

    auto_close = os.environ.get("TOPOSORT_AUTO_CLOSE_MS", "").strip()
    def show_main_window() -> None:
        try:
            from .main_window import MainWindow

            window = MainWindow()
            app.main_window = window
            window.show()
            app.setQuitOnLastWindowClosed(True)
            splash.finish(window)
            ready_marker = os.environ.get("TOPOSORT_STARTUP_READY_FILE", "")
            if ready_marker:
                Path(ready_marker).write_text("ready", encoding="utf-8")
            if auto_close:
                try:
                    delay = max(1, int(auto_close))
                except ValueError:
                    delay = 1000
                QTimer.singleShot(delay, window.close)
        except Exception as exc:
            splash.close()
            QMessageBox.critical(None, "启动失败", f"无法打开应用：\n{exc}")
            app.quit()

    QTimer.singleShot(30, show_main_window)

    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
