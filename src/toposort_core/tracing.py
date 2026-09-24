"""记录一个拓扑排序从零入度候选集到最终顺序的逐步过程。"""

from __future__ import annotations

from .models import DirectedGraph, TraceResult, TraceStep
from .parser import parse_relations
from .solver import find_cycle


def trace_graph(graph: DirectedGraph) -> TraceResult:
    """选择名称最小的当前零入度节点，记录每一步状态。"""
    cycle = find_cycle(graph)
    if cycle:
        return TraceResult(
            steps=(),
            final_order=(),
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            cycle=cycle,
        )

    indegrees = dict(graph.indegrees)
    available = sorted(node for node, degree in indegrees.items() if degree == 0)
    order: list[str] = []
    steps: list[TraceStep] = []

    while available:
        candidates = tuple(available)
        selected = available.pop(0)
        changes: list[tuple[str, int, int]] = []
        newly_available: list[str] = []

        for neighbor in graph.adjacency[selected]:
            before = indegrees[neighbor]
            indegrees[neighbor] = before - 1
            changes.append((neighbor, before, indegrees[neighbor]))
            if indegrees[neighbor] == 0:
                available.append(neighbor)
                newly_available.append(neighbor)

        available.sort()
        order.append(selected)
        steps.append(
            TraceStep(
                candidates=candidates,
                selected=selected,
                indegree_changes=tuple(changes),
                newly_available=tuple(sorted(newly_available)),
                partial_order=tuple(order),
            )
        )

    return TraceResult(
        steps=tuple(steps),
        final_order=tuple(order),
        node_count=graph.node_count,
        edge_count=graph.edge_count,
    )


def trace_text(text: str) -> TraceResult:
    """解析文本并返回逐步说明，保留输入错误和重复关系警告。"""
    parsed = parse_relations(text)
    if not parsed.is_valid:
        return TraceResult(
            steps=(),
            final_order=(),
            node_count=parsed.node_count,
            edge_count=parsed.edge_count,
            errors=parsed.errors,
            warnings=parsed.warnings,
        )
    assert parsed.graph is not None
    traced = trace_graph(parsed.graph)
    return TraceResult(
        steps=traced.steps,
        final_order=traced.final_order,
        node_count=traced.node_count,
        edge_count=traced.edge_count,
        cycle=traced.cycle,
        warnings=parsed.warnings,
    )
