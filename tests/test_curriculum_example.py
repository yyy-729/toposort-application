from __future__ import annotations

from pathlib import Path

from toposort_core import load_relations, plan_stages, solve_graph


def test_verified_curriculum_example_is_valid_and_orders_respect_prerequisites() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parsed = load_relations(project_root / "examples" / "curriculum_2024_verified.txt")

    assert parsed.is_valid
    assert parsed.graph is not None
    assert parsed.node_count == 16
    assert parsed.edge_count == 18
    result = solve_graph(parsed.graph, max_results=100)
    assert result.is_successful
    assert result.output_count == 100
    assert not result.is_complete
    assert result.insights is not None
    assert result.insights.total_order_count == 185_001_600
    for order in result.orders:
        positions = {node: index for index, node in enumerate(order)}
        assert len(order) == parsed.node_count
        assert len(positions) == parsed.node_count
        for source, target in parsed.graph.edges:
            assert positions[source] < positions[target]

    plan = plan_stages(parsed.graph, capacity=4)
    assert plan.is_successful
    assert plan.method == "heuristic"
    assert plan.stage_count == 5
    assert plan.lower_bound == 4
    stage_positions = {
        node: stage_number
        for stage_number, stage in enumerate(plan.stages)
        for node in stage
    }
    assert set(stage_positions) == set(parsed.graph.nodes)
    assert all(len(stage) <= 4 for stage in plan.stages)
    for source, target in parsed.graph.edges:
        assert stage_positions[source] < stage_positions[target]
