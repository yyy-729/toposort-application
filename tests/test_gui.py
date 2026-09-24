from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

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

    def test_graph_canvas_layout_reduction_theme_and_node_selection(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "C"), ("A", "C")])
        canvas.draw_graph(graph, redundant_edges=(("A", "C"),))
        canvas.set_hide_redundant(True)
        self.assertNotIn(("A", "C"), canvas._network.edges)

        for mode in ("spring", "circular", "layered"):
            canvas.set_layout_mode(mode)
            self.assertTrue(canvas.has_graph)
        canvas.set_dark_mode(True)

        axis = canvas.figure.axes[0]
        x, y = axis.transData.transform(canvas._positions["A"])
        canvas._on_mouse_press(SimpleNamespace(inaxes=axis, x=x, y=y))
        self.assertEqual(canvas.selected_node, "A")

    def test_main_window_applies_result(self) -> None:
        window = MainWindow()
        window.input_editor.setPlainText(DEFAULT_SAMPLE)
        parsed = parse_relations(DEFAULT_SAMPLE)
        self.assertIsNotNone(parsed.graph)
        window._current_graph = parsed.graph
        result = solve_text(DEFAULT_SAMPLE)
        window._on_solve_finished(result)

        self.assertEqual(window.order_card.value_label.text(), str(result.output_count))
        self.assertEqual(window.total_card.value_label.text(), "22")
        self.assertEqual(window.level_card.value_label.text(), "4")
        self.assertIn("拓扑排序结果", window.result_editor.toPlainText())
        self.assertIn("分层执行建议", window.insight_editor.toPlainText())
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

    def test_theme_toggle_and_copy_result(self) -> None:
        window = MainWindow()
        window._on_solve_finished(solve_text("<A,C>\n<B,C>"))
        window.theme_button.setChecked(True)
        self.assertEqual(window.theme_button.text(), "浅色模式")

        window.copy_results()
        self.assertIn("拓扑排序结果", QApplication.clipboard().text())
        window.close()

    def test_large_result_is_paged_without_losing_export_or_copy(self) -> None:
        window = MainWindow()
        graph_text = "\n".join(f"<N{i},Z>" for i in range(5))
        result = solve_text(graph_text, max_results=120)
        window._on_solve_finished(result)

        self.assertEqual(result.output_count, 120)
        self.assertEqual(window.page_spin.maximum(), 3)
        self.assertTrue(window.result_pager.isVisibleTo(window.result_tabs))
        self.assertIn("当前显示第 1—50 条", window.result_editor.toPlainText())
        window.page_spin.setValue(3)
        self.assertIn("当前显示第 101—120 条", window.result_editor.toPlainText())
        self.assertIn("120.", window.result_editor.toPlainText())
        window.copy_results()
        self.assertIn("1.", QApplication.clipboard().text())
        self.assertIn("120.", QApplication.clipboard().text())
        window.close()

    def test_stage_planner_runs_and_is_invalidated_on_input_change(self) -> None:
        window = MainWindow()
        text = "<A,C>\n<B,C>"
        parsed = parse_relations(text)
        assert parsed.graph is not None
        window.input_editor.setPlainText(text)
        window._current_graph = parsed.graph
        window.graph_canvas.draw_graph(parsed.graph)
        window._on_solve_finished(solve_text(text))
        self.assertTrue(window.plan_button.isEnabled())

        window.capacity_spin.setValue(2)
        window.run_stage_plan()
        deadline = time.monotonic() + 5
        while window._current_plan is None and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)

        self.assertIsNotNone(window._current_plan)
        assert window._current_plan is not None
        self.assertTrue(window._current_plan.is_optimal)
        self.assertEqual(window._current_plan.stage_count, 2)
        self.assertIn("精确最优", window.plan_editor.toPlainText())
        self.assertTrue(window.export_plan_button.isEnabled())

        window.input_editor.setPlainText(text + "\n<C,D>")
        self.assertIsNone(window._current_plan)
        self.assertFalse(window.export_plan_button.isEnabled())
        window.close()

    def test_clearing_after_stage_plan_does_not_restore_stale_graph(self) -> None:
        window = MainWindow()
        graph_text = "<A,B>"
        parsed = parse_relations(graph_text)
        assert parsed.graph is not None
        window._current_graph = parsed.graph
        window.graph_canvas.draw_graph(parsed.graph)
        window._on_solve_finished(solve_text(graph_text))

        window.clear_all()

        self.assertFalse(window.graph_canvas.has_graph)
        self.assertIsNone(window.graph_canvas._graph)
        self.assertFalse(window.export_graph_button.isEnabled())
        window.close()

    def test_trace_tab_replays_result_and_resets_on_input_change(self) -> None:
        window = MainWindow()
        text = "<A,C>\n<B,C>\n<C,D>"
        parsed = parse_relations(text)
        assert parsed.graph is not None
        window.input_editor.setPlainText(text)
        window._current_graph = parsed.graph
        window.graph_canvas.draw_graph(parsed.graph)
        solved = solve_text(text)
        window._on_solve_finished(solved)
        window.result_tabs.setCurrentIndex(window.trace_tab_index)

        self.assertIn("当前零入度候选：A、B", window.trace_editor.toPlainText())
        self.assertTrue(window.trace_next_button.isEnabled())
        window.trace_next_button.click()
        self.assertIn("第 1 步：选出 A", window.trace_editor.toPlainText())
        self.assertEqual(window.graph_canvas._trace_selected, "A")
        self.assertEqual(window.graph_canvas._trace_completed, {"A"})

        window.trace_play_button.click()
        self.assertTrue(window._trace_timer.isActive())
        window.result_tabs.setCurrentIndex(0)
        self.assertFalse(window._trace_timer.isActive())
        self.assertFalse(window.graph_canvas._trace_candidates)
        window.result_tabs.setCurrentIndex(window.trace_tab_index)
        window.trace_play_button.click()
        self.assertTrue(window._trace_timer.isActive())
        window.trace_play_button.click()
        self.assertFalse(window._trace_timer.isActive())
        while window.trace_next_button.isEnabled():
            window.trace_next_button.click()
        self.assertEqual(window._current_trace.final_order, solved.orders[0])
        self.assertIn("演示完成", window.trace_editor.toPlainText())

        window.input_editor.setPlainText(text + "\n<D,E>")
        self.assertIsNone(window._current_trace)
        self.assertFalse(window.trace_play_button.isEnabled())
        self.assertFalse(window.graph_canvas._trace_candidates)
        window.close()

    def test_cycle_trace_explains_why_playback_cannot_start(self) -> None:
        window = MainWindow()
        text = "<A,B>\n<B,A>"
        parsed = parse_relations(text)
        assert parsed.graph is not None
        window._current_graph = parsed.graph
        window.graph_canvas.draw_graph(parsed.graph)
        window._on_solve_finished(solve_text(text))
        window.result_tabs.setCurrentIndex(window.trace_tab_index)

        self.assertIn("存在有向环", window.trace_editor.toPlainText())
        self.assertFalse(window.trace_play_button.isEnabled())
        window.close()


if __name__ == "__main__":
    unittest.main()
