"""在无界面模式下生成应用预览图。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer

from toposort_app.main import create_application
from toposort_app.main_window import DEFAULT_SAMPLE, MainWindow
from toposort_core import parse_relations, solve_text


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts/app_preview.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    app = create_application([])
    window = MainWindow()
    window.resize(1480, 900)
    window.input_editor.setPlainText(DEFAULT_SAMPLE)
    parsed = parse_relations(DEFAULT_SAMPLE)
    assert parsed.graph is not None
    window._current_graph = parsed.graph
    window.graph_canvas.draw_graph(parsed.graph)
    window._on_solve_finished(solve_text(DEFAULT_SAMPLE))
    if os.environ.get("TOPOSORT_PREVIEW_DARK") == "1":
        window.theme_button.setChecked(True)
    if os.environ.get("TOPOSORT_PREVIEW_TAB") == "insights":
        window.result_tabs.setCurrentIndex(1)
    window.show()

    def capture() -> None:
        window.grab().save(str(output), "PNG")
        window.close()
        app.quit()

    QTimer.singleShot(900, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
