from __future__ import annotations

import math
import unittest

from toposort_core import (
    DirectedGraph,
    analyze_graph,
    compute_levels,
    count_topological_orders,
    find_critical_path,
    find_redundant_edges,
    has_unique_topological_order,
)


class GraphAnalysisTests(unittest.TestCase):
    def test_levels_show_parallel_stages(self) -> None:
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C"), ("C", "D")])

        self.assertEqual(compute_levels(graph), (("A", "B"), ("C",), ("D",)))

    def test_unique_topological_order(self) -> None:
        chain = DirectedGraph.from_edges([("A", "B"), ("B", "C")])
        multiple = DirectedGraph.from_edges([("A", "C"), ("B", "C")])

        self.assertTrue(has_unique_topological_order(chain))
        self.assertFalse(has_unique_topological_order(multiple))

    def test_exact_total_count_uses_dynamic_programming(self) -> None:
        graph = DirectedGraph.from_edges([(node, "Z") for node in "ABCDEFGH"])

        self.assertEqual(count_topological_orders(graph), math.factorial(8))

    def test_large_graph_skips_exact_count(self) -> None:
        graph = DirectedGraph.from_edges([(f"N{index}", "Z") for index in range(19)])

        self.assertIsNone(count_topological_orders(graph))

    def test_critical_path_is_deterministic(self) -> None:
        graph = DirectedGraph.from_edges(
            [("A", "C"), ("B", "C"), ("C", "D"), ("D", "E"), ("C", "F")]
        )

        self.assertEqual(find_critical_path(graph), ("A", "C", "D", "E"))

    def test_redundant_edge_detection(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "C"), ("A", "C")])

        self.assertEqual(find_redundant_edges(graph), (("A", "C"),))

    def test_combined_insights(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "C"), ("A", "C")])
        insights = analyze_graph(graph)

        self.assertEqual(insights.level_count, 3)
        self.assertEqual(insights.max_parallel_width, 1)
        self.assertEqual(insights.total_order_count, 1)
        self.assertTrue(insights.count_is_exact)
        self.assertTrue(insights.is_unique)
        self.assertEqual(insights.redundant_edges, (("A", "C"),))

    def test_cycle_cannot_be_layered(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "A")])

        with self.assertRaisesRegex(ValueError, "有向环"):
            compute_levels(graph)


if __name__ == "__main__":
    unittest.main()
