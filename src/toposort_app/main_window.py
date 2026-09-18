"""拓扑排序应用主窗口。"""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from toposort_core import (
    DirectedGraph,
    SolveResult,
    export_result,
    format_result,
    parse_relations,
)

from .graph_view import GraphCanvas
from .workers import SolverTask

DEFAULT_SAMPLE = """<程序设计基础,数据结构>
<离散数学,数据结构>
<程序设计基础,面向对象程序设计>
<数据结构,算法设计>
<数据结构,数据库原理>
<算法设计,高级算法原理实践>
<数据库原理,高级算法原理实践>
"""


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0") -> None:
        super().__init__()
        self.setProperty("role", "statCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        layout.addWidget(self.value_label)
        layout.addWidget(title_label)

    def set_value(self, value: str | int) -> None:
        self.value_label.setText(str(value))


class MainWindow(QMainWindow):
    """完整桌面应用主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("拓扑序设计器")
        self.resize(1480, 900)
        self.setMinimumSize(1120, 720)

        self._thread_pool = QThreadPool.globalInstance()
        self._current_graph: DirectedGraph | None = None
        self._current_result: SolveResult | None = None
        self._current_file: Path | None = None
        self._active_task: SolverTask | None = None

        self._build_actions()
        self._build_menu()
        self._build_ui()
        self._connect_signals()
        self.load_sample()

    def _build_actions(self) -> None:
        self.open_action = QAction("导入关系文件", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.export_result_action = QAction("导出排序结果", self)
        self.export_result_action.setShortcut(QKeySequence.StandardKey.Save)
        self.export_graph_action = QAction("导出关系图", self)
        self.run_action = QAction("运行分析", self)
        self.run_action.setShortcut(QKeySequence("Ctrl+Return"))
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.about_action = QAction("关于", self)

        self.export_result_action.setEnabled(False)
        self.export_graph_action.setEnabled(False)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_result_action)
        file_menu.addAction(self.export_graph_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        run_menu = self.menuBar().addMenu("运行")
        run_menu.addAction(self.run_action)

        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction(self.about_action)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(22, 18, 22, 16)
        main_layout.setSpacing(14)

        main_layout.addLayout(self._build_header())
        main_layout.addLayout(self._build_command_bar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_input_panel())
        splitter.addWidget(self._build_graph_panel())
        splitter.addWidget(self._build_result_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 6)
        splitter.setStretchFactor(2, 4)
        splitter.setSizes([330, 690, 430])
        main_layout.addWidget(splitter, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        status_bar = QStatusBar()
        status_bar.setSizeGripEnabled(False)
        self.setStatusBar(status_bar)
        self.statusBar().showMessage("就绪")

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        logo = QLabel("拓")
        logo.setObjectName("logoBadge")
        logo.setFixedSize(42, 42)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel("拓扑序设计器")
        title.setObjectName("appTitle")
        subtitle = QLabel("有向关系分析 · 多拓扑序枚举 · 课程先修关系验证")
        subtitle.setObjectName("appSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.status_pill = QLabel("等待运行")
        self.status_pill.setObjectName("statusPill")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(logo)
        layout.addLayout(title_box)
        layout.addStretch()
        layout.addWidget(self.status_pill)
        return layout

    def _build_command_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.import_button = QPushButton("导入 TXT")
        self.sample_button = QPushButton("载入示例")
        self.clear_button = QPushButton("清空")
        self.export_graph_button = QPushButton("导出关系图")
        self.export_result_button = QPushButton("导出结果")
        self.run_button = QPushButton("运行分析")
        self.run_button.setProperty("role", "primary")
        self.run_button.setMinimumWidth(118)

        limit_label = QLabel("结果上限")
        limit_label.setObjectName("mutedText")
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 100000)
        self.limit_spin.setValue(1000)
        self.limit_spin.setSingleStep(100)

        self.export_graph_button.setEnabled(False)
        self.export_result_button.setEnabled(False)

        layout.addWidget(self.import_button)
        layout.addWidget(self.sample_button)
        layout.addWidget(self.clear_button)
        layout.addSpacing(6)
        layout.addWidget(self.export_graph_button)
        layout.addWidget(self.export_result_button)
        layout.addStretch()
        layout.addWidget(limit_label)
        layout.addWidget(self.limit_spin)
        layout.addWidget(self.run_button)
        return layout

    def _new_panel(self) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame()
        panel.setProperty("role", "panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        return panel, layout

    def _build_input_panel(self) -> QFrame:
        panel, layout = self._new_panel()
        panel.setMinimumWidth(290)

        title = QLabel("关系数据")
        title.setObjectName("panelTitle")
        subtitle = QLabel("每行输入一个先后关系")
        subtitle.setObjectName("panelSubtitle")
        self.input_editor = QPlainTextEdit()
        self.input_editor.setPlaceholderText("<前驱节点,后继节点>")
        self.input_editor.setTabChangesFocus(True)

        hint = QLabel("格式示例：<程序设计基础,数据结构>\n必须使用西文尖括号和西文逗号")
        hint.setProperty("role", "hint")
        hint.setWordWrap(True)

        self.input_notice = QLabel("")
        self.input_notice.setProperty("role", "notice")
        self.input_notice.setWordWrap(True)
        self.input_notice.hide()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.input_editor, 1)
        layout.addWidget(hint)
        layout.addWidget(self.input_notice)
        return panel

    def _build_graph_panel(self) -> QFrame:
        panel, layout = self._new_panel()
        title_row = QHBoxLayout()
        title = QLabel("关系图")
        title.setObjectName("panelTitle")
        caption = QLabel("箭头由前驱指向后继")
        caption.setObjectName("panelSubtitle")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(caption)

        self.graph_canvas = GraphCanvas()
        self.graph_toolbar = NavigationToolbar2QT(self.graph_canvas, self)
        self.graph_toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout.addLayout(title_row)
        layout.addWidget(self.graph_toolbar)
        layout.addWidget(self.graph_canvas, 1)
        return panel

    def _build_result_panel(self) -> QFrame:
        panel, layout = self._new_panel()
        panel.setMinimumWidth(350)

        title = QLabel("分析结果")
        title.setObjectName("panelTitle")
        subtitle = QLabel("结果按节点名称稳定排序")
        subtitle.setObjectName("panelSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        cards = QGridLayout()
        cards.setSpacing(8)
        self.node_card = StatCard("节点")
        self.edge_card = StatCard("关系")
        self.order_card = StatCard("结果")
        self.state_card = StatCard("状态", "待运行")
        cards.addWidget(self.node_card, 0, 0)
        cards.addWidget(self.edge_card, 0, 1)
        cards.addWidget(self.order_card, 1, 0)
        cards.addWidget(self.state_card, 1, 1)
        layout.addLayout(cards)

        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setPlaceholderText("运行后在此显示拓扑排序结果")
        layout.addWidget(self.result_editor, 1)
        return panel

    def _connect_signals(self) -> None:
        self.open_action.triggered.connect(self.open_file)
        self.export_result_action.triggered.connect(self.export_results)
        self.export_graph_action.triggered.connect(self.export_graph)
        self.run_action.triggered.connect(self.run_analysis)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self.show_about)

        self.import_button.clicked.connect(self.open_file)
        self.sample_button.clicked.connect(self.load_sample)
        self.clear_button.clicked.connect(self.clear_all)
        self.export_graph_button.clicked.connect(self.export_graph)
        self.export_result_button.clicked.connect(self.export_results)
        self.run_button.clicked.connect(self.run_analysis)
        self.input_editor.textChanged.connect(self._mark_input_changed)

    def _mark_input_changed(self) -> None:
        had_analysis = self._current_graph is not None or bool(self.result_editor.toPlainText())
        self._current_result = None
        self._current_graph = None
        self._set_export_enabled(False)
        self.status_pill.setText("待重新运行")
        if had_analysis:
            self.result_editor.setPlainText("关系数据已修改，请重新运行分析。")
            self.graph_canvas.show_placeholder("数据已修改", "重新运行后生成最新关系图")
            self._update_stats(state="待运行")

    def load_sample(self) -> None:
        self._current_file = None
        self.input_editor.setPlainText(DEFAULT_SAMPLE)
        self.input_notice.hide()
        self.statusBar().showMessage("已载入课程关系示例")

    def clear_all(self) -> None:
        self.input_editor.clear()
        self.result_editor.clear()
        self.input_notice.hide()
        self.graph_canvas.show_placeholder()
        self._current_graph = None
        self._current_result = None
        self._current_file = None
        self._update_stats()
        self._set_export_enabled(False)
        self.status_pill.setText("等待输入")
        self.statusBar().showMessage("已清空")

    def open_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "导入关系数据",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)",
        )
        if not filename:
            return

        path = Path(filename)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            QMessageBox.critical(self, "读取失败", f"无法读取文件：\n{exc}")
            return

        self._current_file = path
        self.input_editor.setPlainText(text)
        self.input_notice.hide()
        self.statusBar().showMessage(f"已导入：{path.name}")

    def run_analysis(self) -> None:
        text = self.input_editor.toPlainText()
        parsed = parse_relations(text)

        if not parsed.is_valid:
            message = "\n".join(str(issue) for issue in parsed.errors)
            self._show_notice(message, error=True)
            self.result_editor.setPlainText("输入格式有误，请修改后重新运行。\n\n" + message)
            self.graph_canvas.show_placeholder("输入格式有误", "请根据左侧提示修改关系数据")
            self._current_graph = None
            self._current_result = None
            self._update_stats(state="格式错误")
            self._set_export_enabled(False)
            self.status_pill.setText("格式错误")
            self.statusBar().showMessage("输入格式错误")
            return

        assert parsed.graph is not None
        self._current_graph = parsed.graph
        self.graph_canvas.draw_graph(parsed.graph)
        self._show_notice(
            "\n".join(str(issue) for issue in parsed.warnings),
            error=False,
        )
        self._update_stats(parsed.graph.node_count, parsed.graph.edge_count, 0, "计算中")
        self._set_busy(True)

        task = SolverTask(text, self.limit_spin.value())
        task.signals.finished.connect(self._on_solve_finished)
        task.signals.failed.connect(self._on_solve_failed)
        self._active_task = task
        self._thread_pool.start(task)

    def _on_solve_finished(self, result: SolveResult) -> None:
        self._current_result = result
        self.result_editor.setPlainText(format_result(result))

        if result.has_cycle and self._current_graph is not None:
            self.graph_canvas.draw_graph(self._current_graph, result.cycle)
            state = "存在环"
            self.status_pill.setText("检测到环")
        elif result.is_complete:
            state = "已完成"
            self.status_pill.setText("全部完成")
        else:
            state = "已截断"
            self.status_pill.setText("达到上限")

        self._update_stats(
            result.node_count,
            result.edge_count,
            result.output_count,
            state,
        )
        self._set_busy(False)
        self._set_export_enabled(True)
        self._active_task = None
        self.statusBar().showMessage("分析完成")

    def _on_solve_failed(self, message: str) -> None:
        self._set_busy(False)
        self._active_task = None
        self.status_pill.setText("运行失败")
        self.statusBar().showMessage("运行失败")
        QMessageBox.critical(self, "运行失败", message)

    def _show_notice(self, message: str, *, error: bool) -> None:
        if not message:
            self.input_notice.hide()
            return
        self.input_notice.setText(message)
        if error:
            self.input_notice.setStyleSheet(
                "color:#9B2C2C;background:#FFF0F0;border:1px solid #F3B7B7;"
                "border-radius:9px;padding:9px;"
            )
        else:
            self.input_notice.setStyleSheet("")
        self.input_notice.show()

    def _set_busy(self, busy: bool) -> None:
        self.progress_bar.setVisible(busy)
        self.run_button.setEnabled(not busy)
        self.run_action.setEnabled(not busy)
        self.open_action.setEnabled(not busy)
        self.import_button.setEnabled(not busy)
        self.sample_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)
        self.limit_spin.setEnabled(not busy)
        self.input_editor.setReadOnly(busy)
        if busy:
            self._set_export_enabled(False)
        if busy:
            self.status_pill.setText("正在计算")
            self.statusBar().showMessage("正在解析关系并枚举拓扑序…")

    def _set_export_enabled(self, enabled: bool) -> None:
        graph_enabled = enabled and self.graph_canvas.has_graph
        result_enabled = enabled and self._current_result is not None
        self.export_graph_button.setEnabled(graph_enabled)
        self.export_graph_action.setEnabled(graph_enabled)
        self.export_result_button.setEnabled(result_enabled)
        self.export_result_action.setEnabled(result_enabled)

    def _update_stats(
        self,
        nodes: int = 0,
        edges: int = 0,
        orders: int = 0,
        state: str = "待运行",
    ) -> None:
        self.node_card.set_value(nodes)
        self.edge_card.set_value(edges)
        self.order_card.set_value(orders)
        self.state_card.set_value(state)

    def export_results(self) -> None:
        if self._current_result is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出拓扑排序结果",
            "拓扑排序结果.txt",
            "文本文件 (*.txt)",
        )
        if not filename:
            return
        try:
            export_result(filename, self._current_result)
        except OSError as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
            return
        self.statusBar().showMessage(f"结果已导出：{Path(filename).name}")

    def export_graph(self) -> None:
        if not self.graph_canvas.has_graph:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出关系图",
            "关系图.png",
            "PNG 图片 (*.png);;SVG 图片 (*.svg);;PDF 文档 (*.pdf)",
        )
        if not filename:
            return
        try:
            self.graph_canvas.export(filename)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
            return
        self.statusBar().showMessage(f"关系图已导出：{Path(filename).name}")

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "关于拓扑序设计器",
            "拓扑序设计器 2.0.0\n\n"
            "高级算法原理实践项目\n"
            "支持有向关系图、多拓扑序枚举、环检测和结果导出。",
        )
