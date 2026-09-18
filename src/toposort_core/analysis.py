"""DAG 的扩展智能分析。"""

from __future__ import annotations

from functools import cache

from .models import DirectedGraph, GraphInsights

EXACT_COUNT_NODE_LIMIT = 18


def compute_levels(graph: DirectedGraph) -> tuple[tuple[str, ...], ...]:
    """使用 Kahn 分层，得到可以并行执行的节点阶段。"""
    indegrees = dict(graph.indegrees)
    available = tuple(sorted(node for node, degree in indegrees.items() if degree == 0))
    levels: list[tuple[str, ...]] = []
    processed = 0

    while available:
        level = available
        levels.append(level)
        processed += len(level)
        next_available: list[str] = []
        for node in level:
            for neighbor in graph.adjacency[node]:
                indegrees[neighbor] -= 1
                if indegrees[neighbor] == 0:
                    next_available.append(neighbor)
        available = tuple(sorted(next_available))

    if processed != graph.node_count:
        raise ValueError("存在有向环，无法进行分层")
    return tuple(levels)


def has_unique_topological_order(graph: DirectedGraph) -> bool:
    """在线性时间内判断 DAG 的拓扑序是否唯一。"""
    indegrees = dict(graph.indegrees)
    available = sorted(node for node, degree in indegrees.items() if degree == 0)
    processed = 0

    while available:
        if len(available) != 1:
            return False
        node = available.pop()
        processed += 1
        for neighbor in graph.adjacency[node]:
            indegrees[neighbor] -= 1
            if indegrees[neighbor] == 0:
                available.append(neighbor)
        available.sort(reverse=True)

    return processed == graph.node_count


def find_critical_path(
    graph: DirectedGraph,
    levels: tuple[tuple[str, ...], ...] | None = None,
) -> tuple[str, ...]:
    """返回节点数量最多的一条依赖链。"""
    if not graph.nodes:
        return ()
    graph_levels = levels if levels is not None else compute_levels(graph)
    order = tuple(node for level in graph_levels for node in level)
    distance = {node: 1 for node in graph.nodes}
    predecessor: dict[str, str] = {}

    for node in order:
        for neighbor in graph.adjacency[node]:
            candidate = distance[node] + 1
            current_predecessor = predecessor.get(neighbor)
            if candidate > distance[neighbor] or (
                candidate == distance[neighbor]
                and (current_predecessor is None or node < current_predecessor)
            ):
                distance[neighbor] = candidate
                predecessor[neighbor] = node

    max_distance = max(distance.values())
    end = min(node for node, value in distance.items() if value == max_distance)
    path = [end]
    while end in predecessor:
        end = predecessor[end]
        path.append(end)
    path.reverse()
    return tuple(path)


def count_topological_orders(
    graph: DirectedGraph,
    max_nodes: int = EXACT_COUNT_NODE_LIMIT,
) -> int | None:
    """使用位掩码动态规划精确统计小规模 DAG 的拓扑序总数。"""
    if graph.node_count > max_nodes:
        return None

    node_indexes = {node: index for index, node in enumerate(graph.nodes)}
    prerequisite_masks = [0] * graph.node_count
    for source, target in graph.edges:
        prerequisite_masks[node_indexes[target]] |= 1 << node_indexes[source]
    full_mask = (1 << graph.node_count) - 1

    @cache
    def count(mask: int) -> int:
        if mask == full_mask:
            return 1
        total = 0
        for index, prerequisite_mask in enumerate(prerequisite_masks):
            bit = 1 << index
            if mask & bit:
                continue
            if prerequisite_mask & ~mask:
                continue
            total += count(mask | bit)
        return total

    return count(0)


def find_redundant_edges(graph: DirectedGraph) -> tuple[tuple[str, str], ...]:
    """找出删除后仍可由其他路径到达的传递冗余边。"""
    redundant: list[tuple[str, str]] = []

    for ignored_edge in graph.edges:
        source, target = ignored_edge
        stack = [source]
        visited = {source}
        reachable = False

        while stack and not reachable:
            node = stack.pop()
            for neighbor in graph.adjacency[node]:
                if (node, neighbor) == ignored_edge:
                    continue
                if neighbor == target:
                    reachable = True
                    break
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        if reachable:
            redundant.append(ignored_edge)

    return tuple(redundant)


def analyze_graph(graph: DirectedGraph) -> GraphInsights:
    """汇总 DAG 的分层、计数、最长链和冗余关系。"""
    levels = compute_levels(graph)
    total_order_count = count_topological_orders(graph)
    return GraphInsights(
        levels=levels,
        critical_path=find_critical_path(graph, levels),
        is_unique=has_unique_topological_order(graph),
        total_order_count=total_order_count,
        count_is_exact=total_order_count is not None,
        redundant_edges=find_redundant_edges(graph),
    )
