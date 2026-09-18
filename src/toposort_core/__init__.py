"""拓扑排序核心模块的公共接口。"""

__version__ = "1.0.0"

from .analysis import (
    EXACT_COUNT_NODE_LIMIT,
    analyze_graph,
    compute_levels,
    count_topological_orders,
    find_critical_path,
    find_redundant_edges,
    has_unique_topological_order,
)
from .io import export_result, format_result, load_relations
from .models import DirectedGraph, GraphInsights, ParseResult, SolveResult, ValidationIssue
from .parser import parse_relations
from .solver import find_cycle, solve_graph, solve_text

__all__ = [
    "DirectedGraph",
    "EXACT_COUNT_NODE_LIMIT",
    "GraphInsights",
    "ParseResult",
    "SolveResult",
    "ValidationIssue",
    "__version__",
    "analyze_graph",
    "compute_levels",
    "count_topological_orders",
    "export_result",
    "find_cycle",
    "find_critical_path",
    "find_redundant_edges",
    "format_result",
    "load_relations",
    "parse_relations",
    "has_unique_topological_order",
    "solve_graph",
    "solve_text",
]
