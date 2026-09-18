from __future__ import annotations

import unittest

from toposort_core import DirectedGraph, find_cycle, solve_graph, solve_text


class SolverTests(unittest.TestCase):
    def assert_valid_order(self, graph: DirectedGraph, order: tuple[str, ...]) -> None:
        self.assertEqual(len(order), graph.node_count)
        self.assertEqual(set(order), set(graph.nodes))
        positions = {node: index for index, node in enumerate(order)}
        self.assertTrue(
            all(positions[source] < positions[target] for source, target in graph.edges)
        )

    def test_chain_has_one_order(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B"), ("B", "C")])
        result = solve_graph(graph)

        self.assertEqual(result.orders, (("A", "B", "C"),))
        self.assertTrue(result.is_complete)
        self.assertEqual(result.stop_reason, "completed")

    def test_diamond_has_two_deterministic_orders(self) -> None:
        graph = DirectedGraph.from_edges(
            [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
        )

        first = solve_graph(graph)
        second = solve_graph(graph)

        self.assertEqual(
            first.orders,
            (("A", "B", "C", "D"), ("A", "C", "B", "D")),
        )
        self.assertEqual(second.orders, first.orders)
        self.assertTrue(first.is_complete)
        for order in first.orders:
            self.assert_valid_order(graph, order)

    def test_disconnected_parts_generate_all_valid_unique_orders(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B"), ("C", "D")])
        result = solve_graph(graph)

        self.assertEqual(result.output_count, 6)
        self.assertEqual(len(set(result.orders)), 6)
        for order in result.orders:
            self.assert_valid_order(graph, order)

    def test_cycle_returns_real_cycle_path(self) -> None:
        graph = DirectedGraph.from_edges(
            [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")]
        )
        result = solve_graph(graph)

        self.assertTrue(result.has_cycle)
        self.assertEqual(result.stop_reason, "cycle")
        self.assertEqual(result.orders, ())
        self.assertEqual(result.cycle[0], result.cycle[-1])
        self.assertTrue(
            all(
                (source, target) in graph.edges
                for source, target in zip(result.cycle[:-1], result.cycle[1:], strict=True)
            )
        )
        self.assertEqual(find_cycle(graph), result.cycle)

    def test_self_loop_is_cycle(self) -> None:
        graph = DirectedGraph.from_edges([("A", "A")])
        result = solve_graph(graph)

        self.assertTrue(result.has_cycle)
        self.assertEqual(result.cycle, ("A", "A"))

    def test_limit_marks_result_incomplete(self) -> None:
        graph = DirectedGraph.from_edges([(node, "Z") for node in "ABCDEFGH"])
        result = solve_graph(graph, max_results=1000)

        self.assertEqual(result.output_count, 1000)
        self.assertFalse(result.is_complete)
        self.assertEqual(result.stop_reason, "limit")
        self.assertEqual(len(set(result.orders)), 1000)

    def test_exact_limit_is_still_complete(self) -> None:
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C")])
        result = solve_graph(graph, max_results=2)

        self.assertEqual(result.output_count, 2)
        self.assertTrue(result.is_complete)
        self.assertEqual(result.stop_reason, "completed")

    def test_smaller_limit_is_incomplete(self) -> None:
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C")])
        result = solve_graph(graph, max_results=1)

        self.assertEqual(result.output_count, 1)
        self.assertFalse(result.is_complete)

    def test_invalid_limit_is_rejected(self) -> None:
        graph = DirectedGraph.from_edges([("A", "B")])
        for value in (0, -1, True, 1.5, "10"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "max_results"):
                solve_graph(graph, max_results=value)  # type: ignore[arg-type]

    def test_solve_text_carries_warnings(self) -> None:
        result = solve_text("<A,C>\n<B,C>\n<A,C>\n")

        self.assertTrue(result.is_successful)
        self.assertEqual(result.output_count, 2)
        self.assertEqual(result.warnings[0].code, "duplicate_edge")

    def test_solve_text_stops_on_parse_error(self) -> None:
        result = solve_text("<A,B>\n<A，C>\n")

        self.assertFalse(result.is_successful)
        self.assertEqual(result.stop_reason, "invalid_input")
        self.assertEqual(result.orders, ())
        self.assertEqual(result.errors[0].line_number, 2)

    def test_empty_graph_has_one_empty_order(self) -> None:
        graph = DirectedGraph.from_edges([])
        result = solve_graph(graph)

        self.assertEqual(result.orders, ((),))
        self.assertTrue(result.is_complete)


if __name__ == "__main__":
    unittest.main()
