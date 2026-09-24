"""测试关系图在长链、长名称和阶段着色下的可读性。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from matplotlib.patches import FancyArrowPatch
from PySide6.QtWidgets import QApplication

from toposort_app.graph_view import GraphCanvas, _wrap_label
from toposort_core import DirectedGraph


class GraphReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_long_chain_uses_rows_instead_of_crushing_onto_one_line(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges(
            [(f"task_node_{index:02d}", f"task_node_{index + 1:02d}") for index in range(1, 30)]
        )
        canvas.draw_graph(graph)

        positions = canvas._positions
        self.assertEqual(len(positions), 30)
        self.assertEqual(len(set(positions.values())), 30)
        self.assertEqual(len({position[1] for position in positions.values()}), 5)
        self.assertEqual(len({position[0] for position in positions.values()}), 6)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "chain.png"
            canvas.export(output)
            self.assertGreater(output.stat().st_size, 5000)

    def test_long_label_preview_is_bounded_but_export_is_complete(self) -> None:
        name = "计算机科学与技术专业基础课程综合实践训练"
        preview = _wrap_label(name, line_width=16, max_lines=2)
        full = _wrap_label(name, line_width=28, max_lines=None)

        self.assertEqual(len(preview.splitlines()), 2)
        self.assertTrue(preview.endswith("…"))
        self.assertEqual(full.replace("\n", ""), name)

    def test_stage_highlight_can_be_cleared_and_new_graph_resets_it(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "C")])
        canvas.draw_graph(graph)
        canvas.set_stage_highlight((("A",), ("B",), ("C",)))
        self.assertEqual(canvas._stage_lookup, {"A": 0, "B": 1, "C": 2})
        self.assertEqual(canvas._node_colors(canvas._network), ["#3157D5", "#7457C8", "#D88727"])

        canvas.set_stage_highlight(None)
        self.assertEqual(canvas._stage_lookup, {})
        canvas.set_stage_highlight((("A",),))
        canvas.draw_graph(graph)
        self.assertEqual(canvas._stage_lookup, {})

    def test_relationship_edges_keep_visible_arrow_artists(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("先修课程", "后续课程")])
        canvas.draw_graph(graph)

        arrows = [
            patch
            for patch in canvas.figure.axes[0].patches
            if isinstance(patch, FancyArrowPatch)
        ]
        self.assertEqual(len(arrows), graph.edge_count)

    def test_long_label_is_selectable_near_its_edge(self) -> None:
        canvas = GraphCanvas()
        long_name = "计算机科学与技术专业基础课程综合实践训练"
        graph = DirectedGraph.from_edges([(long_name, "后续课程")])
        canvas.draw_graph(graph)

        axis = canvas.figure.axes[0]
        artist = canvas._node_artists[long_name]
        bounds = artist.get_window_extent(renderer=canvas.figure.canvas.get_renderer())
        event = SimpleNamespace(
            inaxes=axis,
            x=bounds.x0 + 5,
            y=(bounds.y0 + bounds.y1) / 2,
        )
        canvas._on_mouse_press(event)

        self.assertEqual(canvas.selected_node, long_name)

    def test_trace_highlight_shows_candidates_and_selected_node(self) -> None:
        canvas = GraphCanvas()
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C")])
        canvas.draw_graph(graph)
        canvas.set_trace_highlight(("A", "B"))

        colors = dict(
            zip(canvas._network.nodes, canvas._node_colors(canvas._network), strict=True)
        )
        self.assertEqual(colors["A"], "#22A06B")
        self.assertEqual(colors["B"], "#22A06B")

        canvas.set_trace_highlight(("B",), "A", ("A",))
        colors = dict(
            zip(canvas._network.nodes, canvas._node_colors(canvas._network), strict=True)
        )
        self.assertEqual(colors["A"], "#E5484D")
        self.assertEqual(colors["B"], "#22A06B")

        canvas.set_trace_highlight()
        self.assertFalse(canvas._trace_candidates)
        self.assertEqual(canvas._trace_selected, "")


if __name__ == "__main__":
    unittest.main()
