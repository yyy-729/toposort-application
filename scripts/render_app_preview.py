"""在无界面模式下生成应用预览图。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer

from toposort_app.main import create_application
from toposort_app.main_window import DEFAULT_SAMPLE, MainWindow
from toposort_core import parse_relations, plan_stages, solve_text


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts/app_preview.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    app = create_application([])
    window = MainWindow()
    window.resize(1480, 900)
    input_path = os.environ.get("TOPOSORT_PREVIEW_INPUT", "").strip()
    sample_text = (
        Path(input_path).read_text(encoding="utf-8-sig") if input_path else DEFAULT_SAMPLE
    )
    window.input_editor.setPlainText(sample_text)
    parsed = parse_relations(sample_text)
    assert parsed.graph is not None
    window._current_graph = parsed.graph
    window.graph_canvas.draw_graph(parsed.graph)
    window._on_solve_finished(solve_text(sample_text))
    plan_capacity = os.environ.get("TOPOSORT_PREVIEW_PLAN_CAPACITY", "").strip()
    if plan_capacity:
        window.capacity_spin.setValue(int(plan_capacity))
        window._on_stage_plan_finished(plan_stages(parsed.graph, int(plan_capacity)))
        window.result_tabs.setCurrentIndex(2)
    if os.environ.get("TOPOSORT_PREVIEW_DARK") == "1":
        window.theme_button.setChecked(True)
    preview_tab = os.environ.get("TOPOSORT_PREVIEW_TAB")
    if preview_tab == "insights":
        window.result_tabs.setCurrentIndex(1)
    elif preview_tab == "trace":
        window.result_tabs.setCurrentIndex(window.trace_tab_index)
        trace_step = int(os.environ.get("TOPOSORT_PREVIEW_TRACE_STEP", "2"))
        for _ in range(trace_step):
            window._next_trace_step()
    window.show()
    review_state = os.environ.get("TOPOSORT_PREVIEW_STATE", "")
    about_dialog = None

    def capture() -> None:
        target = window
        if review_state == "layout_popup":
            target = window.layout_combo.view()
        elif review_state == "about" and about_dialog is not None:
            target = about_dialog
        target.grab().save(str(output), "PNG")
        if about_dialog is not None:
            about_dialog.close()
        window.close()
        app.quit()

    def show_review_state() -> None:
        nonlocal about_dialog
        if review_state == "layout_popup":
            window.layout_combo.showPopup()
        elif review_state == "about":
            about_dialog = window._build_about_dialog()
            about_dialog.show()
        QTimer.singleShot(450, capture)

    QTimer.singleShot(450, show_review_state)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
