"""环检测和全部拓扑序枚举。"""

from __future__ import annotations

from .models import DirectedGraph, SolveResult
from .parser import parse_relations


def find_cycle(graph: DirectedGraph) -> tuple[str, ...]:
    """使用迭代式三色深度优先搜索返回一条环路，不存在环时返回空元组。"""
    color = {node: 0 for node in graph.nodes}

    for start in graph.nodes:
        if color[start] != 0:
            continue

        color[start] = 1
        path = [start]
        positions = {start: 0}
        stack: list[tuple[str, int]] = [(start, 0)]

        while stack:
            node, next_index = stack[-1]
            neighbors = graph.adjacency[node]

            if next_index >= len(neighbors):
                stack.pop()
                color[node] = 2
                positions.pop(node)
                path.pop()
                continue

            neighbor = neighbors[next_index]
            stack[-1] = (node, next_index + 1)

            if color[neighbor] == 0:
                color[neighbor] = 1
                positions[neighbor] = len(path)
                path.append(neighbor)
                stack.append((neighbor, 0))
            elif color[neighbor] == 1:
                cycle_start = positions[neighbor]
                return tuple(path[cycle_start:] + [neighbor])

    return ()


def solve_graph(graph: DirectedGraph, max_results: int = 1000) -> SolveResult:
    """枚举图的拓扑序，最多保存 ``max_results`` 条。"""
    if isinstance(max_results, bool) or not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("max_results 必须是大于 0 的整数")

    cycle = find_cycle(graph)
    if cycle:
        return SolveResult(
            orders=(),
            is_complete=False,
            has_cycle=True,
            cycle=cycle,
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            stop_reason="cycle",
        )

    indegrees = dict(graph.indegrees)
    initial_available = tuple(sorted(node for node, degree in indegrees.items() if degree == 0))
    orders: list[tuple[str, ...]] = []
    overflow_found = False

    def backtrack(order: list[str], available: tuple[str, ...]) -> None:
        nonlocal overflow_found
        if overflow_found:
            return

        if len(order) == graph.node_count:
            if len(orders) < max_results:
                orders.append(tuple(order))
            else:
                overflow_found = True
            return

        for index, node in enumerate(available):
            next_available = list(available[:index] + available[index + 1 :])
            changed_neighbors: list[str] = []

            for neighbor in graph.adjacency[node]:
                indegrees[neighbor] -= 1
                changed_neighbors.append(neighbor)
                if indegrees[neighbor] == 0:
                    next_available.append(neighbor)

            next_available.sort()
            order.append(node)
            backtrack(order, tuple(next_available))
            order.pop()

            for neighbor in changed_neighbors:
                indegrees[neighbor] += 1

            if overflow_found:
                return

    backtrack([], initial_available)
    return SolveResult(
        orders=tuple(orders),
        is_complete=not overflow_found,
        has_cycle=False,
        cycle=(),
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        stop_reason="limit" if overflow_found else "completed",
    )


def solve_text(text: str, max_results: int = 1000) -> SolveResult:
    """解析关系文本并求解，是图形界面推荐使用的一站式接口。"""
    parsed = parse_relations(text)
    if not parsed.is_valid:
        return SolveResult(
            orders=(),
            is_complete=False,
            has_cycle=False,
            cycle=(),
            node_count=0,
            edge_count=0,
            stop_reason="invalid_input",
            errors=parsed.errors,
            warnings=parsed.warnings,
        )

    assert parsed.graph is not None
    result = solve_graph(parsed.graph, max_results=max_results)
    return SolveResult(
        orders=result.orders,
        is_complete=result.is_complete,
        has_cycle=result.has_cycle,
        cycle=result.cycle,
        node_count=result.node_count,
        edge_count=result.edge_count,
        stop_reason=result.stop_reason,
        errors=(),
        warnings=parsed.warnings,
    )
