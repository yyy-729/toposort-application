"""文本文件读取和结果导出。"""

from __future__ import annotations

from pathlib import Path

from .models import ParseResult, SolveResult, ValidationIssue
from .parser import parse_relations


def load_relations(path: str | Path) -> ParseResult:
    """以 UTF-8/UTF-8-BOM 读取关系文件。文件错误通过 ParseResult 返回。"""
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        issue = ValidationIssue(
            level="error",
            code="file_read_error",
            message=f"无法读取文件：{exc}",
        )
        return ParseResult(graph=None, errors=(issue,))
    return parse_relations(text)


def format_result(result: SolveResult) -> str:
    """生成适合显示和保存的人类可读文本。"""
    lines = [
        "拓扑排序结果",
        f"节点数：{result.node_count}",
        f"关系数：{result.edge_count}",
    ]

    if result.warnings:
        lines.append("警告：")
        lines.extend(f"- {warning}" for warning in result.warnings)

    if result.errors:
        lines.append("状态：输入格式错误")
        lines.append("错误：")
        lines.extend(f"- {error}" for error in result.errors)
    elif result.has_cycle:
        lines.append("状态：存在有向环，无法进行拓扑排序")
        lines.append(f"检测到的环：{' -> '.join(result.cycle)}")
    else:
        status = "已完成全部枚举" if result.is_complete else "已达到结果上限，未完全枚举"
        lines.append(f"状态：{status}")
        lines.append(f"已输出结果数：{result.output_count}")
        if result.insights is not None:
            total = (
                str(result.insights.total_order_count)
                if result.insights.count_is_exact
                else "节点较多，未进行精确统计"
            )
            lines.extend(
                [
                    f"可行顺序总数：{total}",
                    f"拓扑序唯一：{'是' if result.insights.is_unique else '否'}",
                    f"并行层级数：{result.insights.level_count}",
                    f"最长依赖链：{' -> '.join(result.insights.critical_path)}",
                    f"冗余关系数：{len(result.insights.redundant_edges)}",
                ]
            )
        lines.append("")
        lines.extend(
            f"{index}. {' -> '.join(order)}" for index, order in enumerate(result.orders, start=1)
        )

    return "\n".join(lines) + "\n"


def export_result(path: str | Path, result: SolveResult) -> None:
    """使用 UTF-8 保存求解结果。"""
    Path(path).write_text(format_result(result), encoding="utf-8")
