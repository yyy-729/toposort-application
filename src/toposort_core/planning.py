"""带容量限制的最少阶段规划。

阶段之间严格遵守先后关系；同一阶段只能放置此前阶段已经满足全部依赖的节点。
小图使用状态压缩动态规划求最少阶段数，大图用最长后续依赖链优先的启发式策略。
"""

from __future__ import annotations

from functools import cache
from itertools import combinations

from .analysis import compute_levels
from .models import DirectedGraph, StagePlanResult
from .parser import parse_relations
from .solver import find_cycle

DEFAULT_EXACT_PLAN_NODE_LIMIT = 14
MAX_EXACT_PLAN_NODE_LIMIT = 18


def _validate_options(capacity: int, exact_node_limit: int) -> None:
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
        raise ValueError("capacity 必须是大于 0 的整数")
    if (
        isinstance(exact_node_limit, bool)
        or not isinstance(exact_node_limit, int)
        or not 1 <= exact_node_limit <= MAX_EXACT_PLAN_NODE_LIMIT
    ):
        raise ValueError(f"exact_node_limit 必须是 1 到 {MAX_EXACT_PLAN_NODE_LIMIT} 的整数")


def _prerequisite_masks(graph: DirectedGraph) -> tuple[int, ...]:
    indexes = {node: index for index, node in enumerate(graph.nodes)}
    masks = [0] * graph.node_count
    for source, target in graph.edges:
        masks[indexes[target]] |= 1 << indexes[source]
    return tuple(masks)


def _tail_lengths(graph: DirectedGraph) -> tuple[int, ...]:
    """得到从每个节点出发的最长链长度（包含该节点）。"""
    lengths = {node: 1 for node in graph.nodes}
    levels = compute_levels(graph)
    for level in reversed(levels):
        for node in level:
            lengths[node] = 1 + max(
                (lengths[neighbor] for neighbor in graph.adjacency[node]), default=0
            )
    return tuple(lengths[node] for node in graph.nodes)


def _available_indices(mask: int, masks: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        index
        for index, prerequisites in enumerate(masks)
        if not (mask & (1 << index)) and prerequisites & mask == prerequisites
    )


def _exact_plan(
    graph: DirectedGraph,
    capacity: int,
    masks: tuple[int, ...],
    tails: tuple[int, ...],
) -> tuple[tuple[str, ...], ...]:
    """状态压缩 DP；每步填满当前可选节点或达到容量，不损失最优性。"""
    full_mask = (1 << graph.node_count) - 1
    choices: dict[int, tuple[int, ...]] = {}

    @cache
    def shortest(mask: int) -> int:
        if mask == full_mask:
            return 0

        available = _available_indices(mask, masks)
        take = min(capacity, len(available))
        # 优先尝试最长后续依赖链，常可提前命中下界并减少搜索。
        prioritized = tuple(
            sorted(available, key=lambda index: (-tails[index], graph.nodes[index]))
        )
        remaining = graph.node_count - mask.bit_count()
        lower_bound = max(
            (remaining + capacity - 1) // capacity,
            max(tails[index] for index in range(graph.node_count) if not mask & (1 << index)),
        )
        best = graph.node_count + 1
        best_group: tuple[int, ...] = ()
        for group in combinations(prioritized, take):
            next_mask = mask
            for index in group:
                next_mask |= 1 << index
            candidate = 1 + shortest(next_mask)
            if candidate < best:
                best = candidate
                best_group = group
                if best == lower_bound:
                    break
        choices[mask] = best_group
        return best

    shortest(0)
    stages: list[tuple[str, ...]] = []
    mask = 0
    while mask != full_mask:
        group = choices[mask]
        stages.append(tuple(sorted(graph.nodes[index] for index in group)))
        for index in group:
            mask |= 1 << index
    return tuple(stages)


def _heuristic_plan(
    graph: DirectedGraph,
    capacity: int,
    masks: tuple[int, ...],
    tails: tuple[int, ...],
) -> tuple[tuple[str, ...], ...]:
    full_mask = (1 << graph.node_count) - 1
    mask = 0
    stages: list[tuple[str, ...]] = []

    while mask != full_mask:
        available = _available_indices(mask, masks)
        prioritized = sorted(available, key=lambda index: (-tails[index], graph.nodes[index]))
        group = prioritized[:capacity]
        stages.append(tuple(sorted(graph.nodes[index] for index in group)))
        for index in group:
            mask |= 1 << index

    return tuple(stages)


def plan_stages(
    graph: DirectedGraph,
    capacity: int,
    exact_node_limit: int = DEFAULT_EXACT_PLAN_NODE_LIMIT,
) -> StagePlanResult:
    """规划 DAG 的阶段，严格限制每阶段节点数。

    对于节点数不超过 ``exact_node_limit`` 的图，结果为精确最优；更大图
    使用关键链优先的启发式建议，不能保证最优。存在环时不产生方案。
    """
    _validate_options(capacity, exact_node_limit)
    cycle = find_cycle(graph)
    if cycle:
        return StagePlanResult(
            stages=(),
            capacity=capacity,
            method="unavailable",
            is_optimal=False,
            lower_bound=0,
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            cycle=cycle,
        )

    masks = _prerequisite_masks(graph)
    tails = _tail_lengths(graph)
    lower_bound = max(
        (graph.node_count + capacity - 1) // capacity,
        max(tails, default=0),
    )
    use_exact = graph.node_count <= exact_node_limit
    stages = (
        _exact_plan(graph, capacity, masks, tails)
        if use_exact
        else _heuristic_plan(graph, capacity, masks, tails)
    )
    return StagePlanResult(
        stages=stages,
        capacity=capacity,
        method="exact" if use_exact else "heuristic",
        is_optimal=use_exact,
        lower_bound=lower_bound,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
    )


def plan_text(
    text: str,
    capacity: int,
    exact_node_limit: int = DEFAULT_EXACT_PLAN_NODE_LIMIT,
) -> StagePlanResult:
    """解析关系文本并规划阶段，供图形界面直接调用。"""
    _validate_options(capacity, exact_node_limit)
    parsed = parse_relations(text)
    if not parsed.is_valid:
        return StagePlanResult(
            stages=(),
            capacity=capacity,
            method="unavailable",
            is_optimal=False,
            lower_bound=0,
            node_count=parsed.node_count,
            edge_count=parsed.edge_count,
            errors=parsed.errors,
            warnings=parsed.warnings,
        )
    assert parsed.graph is not None
    result = plan_stages(parsed.graph, capacity, exact_node_limit)
    return StagePlanResult(
        stages=result.stages,
        capacity=result.capacity,
        method=result.method,
        is_optimal=result.is_optimal,
        lower_bound=result.lower_bound,
        node_count=result.node_count,
        edge_count=result.edge_count,
        cycle=result.cycle,
        warnings=parsed.warnings,
    )
