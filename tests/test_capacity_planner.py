from __future__ import annotations

import random
from collections import deque
from itertools import combinations

import pytest

from toposort_core import DirectedGraph, plan_stages, plan_text


def assert_valid_plan(
    graph: DirectedGraph,
    stages: tuple[tuple[str, ...], ...],
    capacity: int,
) -> None:
    positions = {node: stage for stage, nodes in enumerate(stages) for node in nodes}
    assert set(positions) == set(graph.nodes)
    assert sum(len(nodes) for nodes in stages) == graph.node_count
    assert all(0 < len(nodes) <= capacity for nodes in stages)
    assert all(positions[source] < positions[target] for source, target in graph.edges)


def brute_minimum_stages(graph: DirectedGraph, capacity: int) -> int:
    """与正式实现独立的小图广度优先搜索基准。"""
    indexes = {node: index for index, node in enumerate(graph.nodes)}
    prerequisites = [0] * graph.node_count
    for source, target in graph.edges:
        prerequisites[indexes[target]] |= 1 << indexes[source]
    full = (1 << graph.node_count) - 1
    queue = deque([(0, 0)])
    visited = {0}
    while queue:
        mask, count = queue.popleft()
        if mask == full:
            return count
        available = [
            index
            for index, required in enumerate(prerequisites)
            if not mask & (1 << index) and required & mask == required
        ]
        for size in range(1, min(capacity, len(available)) + 1):
            for group in combinations(available, size):
                next_mask = mask | sum(1 << index for index in group)
                if next_mask not in visited:
                    visited.add(next_mask)
                    queue.append((next_mask, count + 1))
    raise AssertionError("测试图不应存在环")


def test_exact_plan_is_minimum_and_respects_constraints() -> None:
    graph = DirectedGraph.from_edges(
        [("A", "D"), ("B", "D"), ("C", "E"), ("D", "F"), ("E", "F")]
    )
    result = plan_stages(graph, capacity=2)

    assert result.is_successful
    assert result.method == "exact"
    assert result.is_optimal
    assert result.stage_count == brute_minimum_stages(graph, 2)
    assert result.lower_bound <= result.stage_count
    assert_valid_plan(graph, result.stages, 2)
    assert result == plan_stages(graph, capacity=2)


def test_exact_plan_matches_independent_bruteforce_on_many_dags() -> None:
    rng = random.Random(20260922)
    nodes = "ABCDEF"
    for _ in range(30):
        edges = [(node, "F") for node in nodes[:-1]]
        edges.extend(
            (left, right)
            for index, left in enumerate(nodes[:-1])
            for right in nodes[index + 1 : -1]
            if rng.random() < 0.3
        )
        graph = DirectedGraph.from_edges(edges)
        capacity = rng.randint(1, 4)
        result = plan_stages(graph, capacity)
        assert result.stage_count == brute_minimum_stages(graph, capacity)
        assert_valid_plan(graph, result.stages, capacity)


def test_capacity_one_and_unlimited_capacity() -> None:
    graph = DirectedGraph.from_edges([("A", "C"), ("B", "C"), ("C", "D")])
    one = plan_stages(graph, 1)
    wide = plan_stages(graph, 100)

    assert all(len(stage) == 1 for stage in one.stages)
    assert_valid_plan(graph, one.stages, 1)
    assert wide.stages == (("A", "B"), ("C",), ("D",))
    assert wide.stage_count == wide.lower_bound


def test_large_graph_uses_explicit_heuristic_label() -> None:
    graph = DirectedGraph.from_edges([(f"课程{index:02d}", "毕业设计") for index in range(15)])
    result = plan_stages(graph, 4)

    assert result.method == "heuristic"
    assert not result.is_optimal
    assert result.stage_count >= result.lower_bound
    assert_valid_plan(graph, result.stages, 4)
    assert result == plan_stages(graph, 4)


def test_exact_plan_can_exceed_simple_lower_bound() -> None:
    graph = DirectedGraph.from_edges([(f"N{index:02d}", "Z") for index in range(13)])
    result = plan_stages(graph, 7)

    assert result.method == "exact"
    assert result.lower_bound == 2
    assert result.stage_count == 3
    assert_valid_plan(graph, result.stages, 7)


def test_graph_with_cycle_does_not_generate_plan() -> None:
    graph = DirectedGraph.from_edges([("A", "B"), ("B", "A")])
    result = plan_stages(graph, 2)

    assert not result.is_successful
    assert result.method == "unavailable"
    assert result.stages == ()
    assert result.cycle == ("A", "B", "A")


def test_text_interface_keeps_parse_errors() -> None:
    result = plan_text("<A,B>\n<A，C>", 2)

    assert not result.is_successful
    assert result.method == "unavailable"
    assert result.stages == ()
    assert result.errors[0].line_number == 2


def test_text_interface_keeps_duplicate_warnings() -> None:
    result = plan_text("<A,B>\n<A,B>", 2)

    assert result.is_successful
    assert len(result.warnings) == 1
    assert result.edge_count == 1


def test_empty_graph_is_valid_zero_stage_plan() -> None:
    result = plan_stages(DirectedGraph.from_edges([]), 2)

    assert result.is_successful
    assert result.is_optimal
    assert result.stage_count == 0
    assert result.lower_bound == 0


@pytest.mark.parametrize("capacity", [0, -1, 1.5, True, "2"])
def test_capacity_must_be_positive_integer(capacity: object) -> None:
    with pytest.raises(ValueError, match="capacity"):
        plan_text("<A,B>", capacity)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [0, 19, 1.5, True])
def test_exact_limit_is_bounded(limit: object) -> None:
    with pytest.raises(ValueError, match="exact_node_limit"):
        plan_text("<A,B>", 2, limit)  # type: ignore[arg-type]
