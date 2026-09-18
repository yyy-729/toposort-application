"""命令行演示入口。"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from .io import export_result, format_result, load_relations
from .solver import solve_graph


def _positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("结果上限必须是整数") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("结果上限必须大于 0")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="读取关系文件并枚举拓扑排序结果")
    parser.add_argument("input", type=Path, help="输入 TXT 文件")
    parser.add_argument("--limit", type=_positive_integer, default=1000, help="结果上限")
    parser.add_argument("--output", type=Path, help="结果 TXT 文件")
    return parser


def _configure_console_encoding() -> None:
    """让 Windows 控制台稳定显示中文。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    _configure_console_encoding()
    args = build_parser().parse_args(argv)
    parsed = load_relations(args.input)

    if parsed.errors:
        for issue in parsed.errors:
            print(issue, file=sys.stderr)
        if any(issue.code == "file_read_error" for issue in parsed.errors):
            return 4
        return 2

    if parsed.graph is None:  # 防御性分支，正常情况下不会到达
        print("输入解析失败", file=sys.stderr)
        return 2

    result = solve_graph(parsed.graph, max_results=args.limit)
    result = replace(result, warnings=parsed.warnings)
    print(format_result(result), end="")

    if args.output is not None:
        try:
            export_result(args.output, result)
        except OSError as exc:
            print(f"无法写入结果文件：{exc}", file=sys.stderr)
            return 4

    return 3 if result.has_cycle else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
