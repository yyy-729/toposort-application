from __future__ import annotations

from toposort_core import DirectedGraph, solve_graph, trace_graph, trace_text


def test_trace_replays_first_topological_order_with_valid_indegrees() -> None:
    graph = DirectedGraph.from_edges(
        [("A", "C"), ("B", "C"), ("C", "D"), ("B", "E")]
    )
    original_indegrees = dict(graph.indegrees)
    traced = trace_graph(graph)
    solved = solve_graph(graph)

    assert traced.is_successful
    assert len(traced.steps) == graph.node_count
    assert traced.final_order == solved.orders[0]
    assert dict(graph.indegrees) == original_indegrees

    remaining_indegrees = dict(original_indegrees)
    available = sorted(node for node, degree in remaining_indegrees.items() if degree == 0)
    partial: list[str] = []
    for step in traced.steps:
        assert step.candidates == tuple(available)
        assert step.selected == available.pop(0)
        changed = []
        newly_available = []
        for neighbor in graph.adjacency[step.selected]:
            before = remaining_indegrees[neighbor]
            remaining_indegrees[neighbor] -= 1
            changed.append((neighbor, before, remaining_indegrees[neighbor]))
            if remaining_indegrees[neighbor] == 0:
                available.append(neighbor)
                newly_available.append(neighbor)
        available.sort()
        partial.append(step.selected)
        assert step.indegree_changes == tuple(changed)
        assert step.newly_available == tuple(sorted(newly_available))
        assert step.partial_order == tuple(partial)

    assert not available
    assert all(degree == 0 for degree in remaining_indegrees.values())


def test_cycle_stops_trace_with_concrete_cycle() -> None:
    traced = trace_text("<A,B>\n<B,C>\n<C,A>")

    assert not traced.is_successful
    assert traced.steps == ()
    assert traced.final_order == ()
    assert traced.cycle[0] == traced.cycle[-1]


def test_trace_preserves_parse_errors_and_duplicate_warning() -> None:
    invalid = trace_text("<A，B>")
    duplicated = trace_text("<A,B>\n<A,B>")

    assert invalid.errors[0].line_number == 1
    assert invalid.steps == ()
    assert duplicated.is_successful
    assert len(duplicated.warnings) == 1
    assert duplicated.final_order == ("A", "B")
