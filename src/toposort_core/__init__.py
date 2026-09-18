"""拓扑排序核心模块的公共接口。"""

__version__ = "1.0.0"

from .io import export_result, format_result, load_relations
from .models import DirectedGraph, ParseResult, SolveResult, ValidationIssue
from .parser import parse_relations
from .solver import find_cycle, solve_graph, solve_text

__all__ = [
    "DirectedGraph",
    "ParseResult",
    "SolveResult",
    "ValidationIssue",
    "__version__",
    "export_result",
    "find_cycle",
    "format_result",
    "load_relations",
    "parse_relations",
    "solve_graph",
    "solve_text",
]
