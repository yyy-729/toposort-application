from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from toposort_app.graph_view import GraphCanvas
from toposort_app.main_window import DEFAULT_SAMPLE, MainWindow
from toposort_core import DirectedGraph, parse_relations, solve_text


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_graph_canvas_draws_and_exports(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C")])
        canvas.draw_graph(graph)

        with tempfile.TemporaryDirectory() as directory:
            for suffix in (".png", ".svg", ".pdf"):
                with self.subTest(suffix=suffix):
                    output = Path(directory) / f"graph{suffix}"
                    canvas.export(output)
                    self.assertGreater(output.stat().st_size, 1000)

    def test_graph_canvas_highlights_cycle(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "A")])
        canvas.draw_graph(graph)
        canvas.draw_graph(graph, ("A", "B", "A"))
        self.assertTrue(canvas.has_graph)

    def test_main_window_applies_result(self) -> None:
        window = MainWindow()
        window.input_editor.setPlainText(DEFAULT_SAMPLE)
        parsed = parse_relations(DEFAULT_SAMPLE)
        self.assertIsNotNone(parsed.graph)
        window._current_graph = parsed.graph
        result = solve_text(DEFAULT_SAMPLE)
        window._on_solve_finished(result)

        self.assertEqual(window.order_card.value_label.text(), str(result.output_count))
        self.assertIn("拓扑排序结果", window.result_editor.toPlainText())
        self.assertTrue(window.export_result_button.isEnabled())
        window.close()

    def test_invalid_input_updates_window_state(self) -> None:
        window = MainWindow()
        window.input_editor.setPlainText("<A，B>")
        window.run_analysis()

        self.assertEqual(window.state_card.value_label.text(), "格式错误")
        self.assertTrue(window.input_notice.isVisibleTo(window))
        self.assertIn("第 1 行", window.result_editor.toPlainText())
        window.close()

    def test_main_window_runs_background_analysis(self) -> None:
        window = MainWindow()
        window.input_editor.setPlainText("<A,C>\n<B,C>")
        window.run_analysis()

        deadline = time.monotonic() + 5
        while window._current_result is None and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)

        self.assertIsNotNone(window._current_result)
        assert window._current_result is not None
        self.assertEqual(window._current_result.output_count, 2)
        self.assertEqual(window.state_card.value_label.text(), "已完成")
        self.assertFalse(window.input_editor.isReadOnly())
        window.close()

    def test_background_cycle_analysis_does_not_break_graph(self) -> None:
        window = MainWindow()
        window.input_editor.setPlainText("<A,B>\n<B,C>\n<C,A>")
        window.run_analysis()

        deadline = time.monotonic() + 5
        while window._current_result is None and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)

        self.assertIsNotNone(window._current_result)
        assert window._current_result is not None
        self.assertTrue(window._current_result.has_cycle)
        self.assertEqual(window.state_card.value_label.text(), "存在环")
        self.assertTrue(window.graph_canvas.has_graph)
        window.close()

    def test_editing_after_analysis_invalidates_old_exports(self) -> None:
        window = MainWindow()
        parsed = parse_relations(DEFAULT_SAMPLE)
        assert parsed.graph is not None
        window._current_graph = parsed.graph
        window.graph_canvas.draw_graph(parsed.graph)
        window._on_solve_finished(solve_text(DEFAULT_SAMPLE))
        self.assertTrue(window.export_result_button.isEnabled())

        window.input_editor.setPlainText(DEFAULT_SAMPLE + "<测试节点,高级算法原理实践>\n")

        self.assertFalse(window.export_result_button.isEnabled())
        self.assertFalse(window.export_graph_button.isEnabled())
        self.assertEqual(window.state_card.value_label.text(), "待运行")
        window.close()


if __name__ == "__main__":
    unittest.main()
