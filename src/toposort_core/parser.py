"""任务书规定的 ``<前驱,后继>`` 关系解析。"""

from __future__ import annotations

from .models import DirectedGraph, ParseResult, ValidationIssue


def _error(line_number: int | None, code: str, message: str, raw_line: str = "") -> ValidationIssue:
    return ValidationIssue(
        level="error",
        code=code,
        message=message,
        line_number=line_number,
        raw_line=raw_line,
    )


def parse_relations(text: str) -> ParseResult:
    """解析一行一个的关系文本。

    只接受任务书要求的西文尖括号和西文逗号。只要存在格式错误，结果中的
    ``graph`` 就为 ``None``，调用方不得继续求解。
    """
    if text.startswith("\ufeff"):
        text = text.removeprefix("\ufeff")

    edges: list[tuple[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        if "，" in stripped:
            errors.append(
                _error(
                    line_number,
                    "chinese_comma",
                    "必须使用西文逗号 ','，不能使用中文逗号 '，'",
                    raw_line,
                )
            )
            continue

        if not stripped.startswith("<") or not stripped.endswith(">"):
            errors.append(
                _error(
                    line_number,
                    "missing_brackets",
                    "关系必须使用西文尖括号，格式为 <前驱,后继>",
                    raw_line,
                )
            )
            continue

        inner = stripped[1:-1]
        if inner.count(",") != 1:
            errors.append(
                _error(
                    line_number,
                    "invalid_field_count",
                    "每行必须且只能包含两个节点，中间使用一个西文逗号",
                    raw_line,
                )
            )
            continue

        source, target = (part.strip() for part in inner.split(",", maxsplit=1))
        if not source or not target:
            errors.append(
                _error(
                    line_number,
                    "empty_node",
                    "前驱节点和后继节点都不能为空",
                    raw_line,
                )
            )
            continue

        if any(symbol in source or symbol in target for symbol in "<>，"):
            errors.append(
                _error(
                    line_number,
                    "invalid_node",
                    "节点名称中不能包含尖括号、逗号等关系分隔符",
                    raw_line,
                )
            )
            continue

        edge = (source, target)
        if edge in seen_edges:
            warnings.append(
                ValidationIssue(
                    level="warning",
                    code="duplicate_edge",
                    message=f"重复关系 <{source},{target}> 已忽略",
                    line_number=line_number,
                    raw_line=raw_line,
                )
            )
            continue

        seen_edges.add(edge)
        edges.append(edge)

    if not edges and not errors:
        errors.append(_error(None, "empty_input", "输入中没有任何有效关系"))

    graph = DirectedGraph.from_edges(edges) if not errors else None
    return ParseResult(graph=graph, errors=tuple(errors), warnings=tuple(warnings))

