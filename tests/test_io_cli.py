from __future__ import annotations

import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from toposort_core import DirectedGraph, export_result, format_result, solve_graph, solve_text
from toposort_core.cli import _positive_integer, main


class IoAndCliTests(unittest.TestCase):
    def test_format_completed_result(self) -> None:
        result = solve_text("<A,C>\n<B,C>\n")
        text = format_result(result)

        self.assertIn("状态：已完成全部枚举", text)
        self.assertIn("已输出结果数：2", text)
        self.assertIn("1. A -> B -> C", text)

    def test_format_truncated_result(self) -> None:
        graph = DirectedGraph.from_edges([("A", "C"), ("B", "C")])
        text = format_result(solve_graph(graph, max_results=1))

        self.assertIn("未完全枚举", text)

    def test_format_cycle_result(self) -> None:
        text = format_result(solve_text("<A,B>\n<B,A>\n"))

        self.assertIn("存在有向环", text)
        self.assertIn("A -> B -> A", text)

    def test_format_error_and_warning(self) -> None:
        error_text = format_result(solve_text("<A，B>\n"))
        warning_text = format_result(solve_text("<A,B>\n<A,B>\n"))

        self.assertIn("输入格式错误", error_text)
        self.assertIn("第 1 行", error_text)
        self.assertIn("警告", warning_text)
        self.assertIn("重复关系", warning_text)

    def test_export_result_writes_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "结果.txt"
            export_result(output, solve_text("<课程一,课程二>\n"))
            content = output.read_text(encoding="utf-8")

        self.assertIn("课程一 -> 课程二", content)

    def test_cli_success_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "multiple.txt"
            output = Path(directory) / "result.txt"
            source.write_text("<A,C>\n<B,C>\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main([str(source), "--limit", "1000", "--output", str(output)])

            self.assertTrue(output.exists())

        self.assertEqual(code, 0)
        self.assertIn("已完成全部枚举", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_cli_parse_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.txt"
            source.write_text("<A，B>\n", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main([str(source)])

        self.assertEqual(code, 2)
        self.assertIn("第 1 行", stderr.getvalue())

    def test_cli_cycle_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "cycle.txt"
            source.write_text("<A,B>\n<B,A>\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([str(source)])

        self.assertEqual(code, 3)
        self.assertIn("存在有向环", stdout.getvalue())

    def test_cli_missing_file_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main([str(Path(directory) / "missing.txt")])

        self.assertEqual(code, 4)
        self.assertIn("无法读取文件", stderr.getvalue())

    def test_cli_write_error_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "chain.txt"
            source.write_text("<A,B>\n", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                code = main([str(source), "--output", directory])

        self.assertEqual(code, 4)
        self.assertIn("无法写入结果文件", stderr.getvalue())

    def test_positive_integer(self) -> None:
        self.assertEqual(_positive_integer("5"), 5)
        for value in ("0", "-1", "abc"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                _positive_integer(value)


if __name__ == "__main__":
    unittest.main()
