"""核心数据类型。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

IssueLevel = Literal["error", "warning"]
StopReason = Literal["completed", "limit", "cycle", "invalid_input"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """输入解析过程中发现的问题。"""

    level: IssueLevel
    code: str
    message: str
    line_number: int | None = None
    raw_line: str = ""

    def __str__(self) -> str:
        location = f"第 {self.line_number} 行：" if self.line_number is not None else ""
        return f"{location}{self.message}"


@dataclass(frozen=True, slots=True)
class DirectedGraph:
    """不可变的有向图数据。"""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    adjacency: Mapping[str, tuple[str, ...]]
    indegrees: Mapping[str, int]

    @classmethod
    def from_edges(
        cls, edges: list[tuple[str, str]] | tuple[tuple[str, str], ...]
    ) -> DirectedGraph:
        """根据边集合建立节点、邻接表和入度表。"""
        unique_edges = tuple(sorted(set(edges)))
        nodes = tuple(sorted({node for edge in unique_edges for node in edge}))
        adjacency_lists: dict[str, list[str]] = {node: [] for node in nodes}
        indegrees = {node: 0 for node in nodes}

        for source, target in unique_edges:
            adjacency_lists[source].append(target)
            indegrees[target] += 1

        adjacency = {
            node: tuple(sorted(neighbors)) for node, neighbors in adjacency_lists.items()
        }
        return cls(
            nodes=nodes,
            edges=unique_edges,
            adjacency=MappingProxyType(adjacency),
            indegrees=MappingProxyType(indegrees),
        )

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


@dataclass(frozen=True, slots=True)
class ParseResult:
    """关系文本解析结果。"""

    graph: DirectedGraph | None
    errors: tuple[ValidationIssue, ...] = ()
    warnings: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.graph is not None and not self.errors

    @property
    def node_count(self) -> int:
        return self.graph.node_count if self.graph is not None else 0

    @property
    def edge_count(self) -> int:
        return self.graph.edge_count if self.graph is not None else 0


@dataclass(frozen=True, slots=True)
class GraphInsights:
    """从 DAG 中得到的智能分析结果。"""

    levels: tuple[tuple[str, ...], ...]
    critical_path: tuple[str, ...]
    is_unique: bool
    total_order_count: int | None
    count_is_exact: bool
    redundant_edges: tuple[tuple[str, str], ...]

    @property
    def level_count(self) -> int:
        return len(self.levels)

    @property
    def max_parallel_width(self) -> int:
        return max((len(level) for level in self.levels), default=0)


@dataclass(frozen=True, slots=True)
class SolveResult:
    """拓扑排序求解结果。"""

    orders: tuple[tuple[str, ...], ...]
    is_complete: bool
    has_cycle: bool
    cycle: tuple[str, ...]
    node_count: int
    edge_count: int
    stop_reason: StopReason
    errors: tuple[ValidationIssue, ...] = ()
    warnings: tuple[ValidationIssue, ...] = ()
    insights: GraphInsights | None = None

    @property
    def output_count(self) -> int:
        return len(self.orders)

    @property
    def is_successful(self) -> bool:
        return not self.errors and not self.has_cycle
