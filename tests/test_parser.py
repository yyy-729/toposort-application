from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from toposort_core import load_relations, parse_relations


class ParserTests(unittest.TestCase):
    def test_parse_english_chinese_spaces_blank_and_bom(self) -> None:
        result = parse_relations("\ufeff  <离散数学, 数据结构>  \n\n<数据结构,算法设计>\n")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.node_count, 3)
        self.assertEqual(result.edge_count, 2)
        self.assertIsNotNone(result.graph)
        assert result.graph is not None
        self.assertEqual(
            result.graph.edges,
            (("数据结构", "算法设计"), ("离散数学", "数据结构")),
        )

    def test_duplicate_edge_is_warning_and_is_not_counted_twice(self) -> None:
        result = parse_relations("<A,B>\n<A,B>\n")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.edge_count, 1)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0].code, "duplicate_edge")
        self.assertEqual(result.warnings[0].line_number, 2)

    def test_invalid_lines_report_all_line_numbers(self) -> None:
        result = parse_relations("<A，B>\nA,B\n<A,>\n<A,B,C>\n<<A,B>>\n")

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.graph)
        self.assertEqual([issue.line_number for issue in result.errors], [1, 2, 3, 4, 5])
        self.assertEqual(
            [issue.code for issue in result.errors],
            [
                "chinese_comma",
                "missing_brackets",
                "empty_node",
                "invalid_field_count",
                "invalid_node",
            ],
        )

    def test_empty_input_is_error(self) -> None:
        result = parse_relations("\n   \n")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "empty_input")
        self.assertIsNone(result.errors[0].line_number)

    def test_load_relations_supports_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "relations.txt"
            source.write_text("<课程一,课程二>\n", encoding="utf-8-sig")

            result = load_relations(source)

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.graph)
        assert result.graph is not None
        self.assertEqual(result.graph.edges, (("课程一", "课程二"),))

    def test_load_relations_returns_file_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = load_relations(Path(directory) / "missing.txt")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "file_read_error")

    def test_load_relations_returns_encoding_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.txt"
            source.write_bytes(b"\xff\xfe\x00")
            result = load_relations(source)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "file_read_error")


if __name__ == "__main__":
    unittest.main()

