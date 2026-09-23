"""拓扑排序应用主窗口。"""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import Qt, QThreadPool, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from toposort_core import (
    DirectedGraph,
    SolveResult,
    StagePlanResult,
    export_result,
    format_result,
    parse_relations,
)

from .graph_view import GraphCanvas
from .theme import APP_STYLESHEET, DARK_STYLESHEET
from .workers import PlannerTask, SolverTask

DEFAULT_SAMPLE = """<程序设计基础,数据结构>
<离散数学,数据结构>
<程序设计基础,面向对象程序设计>
<数据结构,算法设计>
<程序设计基础,算法设计>
<数据结构,数据库原理>
<算法设计,高级算法原理实践>
<数据库原理,高级算法原理实践>
"""

RESULTS_PER_PAGE = 50


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
        self._active_plan_task: PlannerTask | None = None
        self._current_plan: StagePlanResult | None = None
        self._dark_mode = False

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
        self.manual_action = QAction("使用说明", self)

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
        help_menu.addAction(self.manual_action)
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

        self.theme_button = QPushButton("深色模式")
        self.theme_button.setCheckable(True)
        self.theme_button.setToolTip("切换深色或浅色主题")

        layout.addWidget(logo)
        layout.addLayout(title_box)
        layout.addStretch()
        layout.addWidget(self.theme_button)
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
        self.layout_combo = QComboBox()
        self.layout_combo.addItem("分层布局", "layered")
        self.layout_combo.addItem("力导向布局", "spring")
        self.layout_combo.addItem("环形布局", "circular")
        self.layout_combo.setToolTip("切换关系图布局")
        self.reduction_check = QCheckBox("隐藏冗余边")
        self.reduction_check.setToolTip("隐藏可由其他路径推导出的关系，不改变先后约束")
        self.reduction_check.setEnabled(False)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(caption)
        title_row.addWidget(self.layout_combo)
        title_row.addWidget(self.reduction_check)

        self.graph_canvas = GraphCanvas()
        self.graph_toolbar = NavigationToolbar2QT(self.graph_canvas, self)
        self.graph_toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.node_detail = QLabel("点击图中节点，可高亮它的全部前置和后续节点")
        self.node_detail.setProperty("role", "hint")
        self.node_detail.setWordWrap(True)

        layout.addLayout(title_row)
        layout.addWidget(self.graph_toolbar)
        layout.addWidget(self.graph_canvas, 1)
        layout.addWidget(self.node_detail)
        return panel

    def _build_result_panel(self) -> QFrame:
        panel, layout = self._new_panel()
        panel.setMinimumWidth(350)

        title_row = QHBoxLayout()
        title = QLabel("分析结果")
        title.setObjectName("panelTitle")
        self.copy_result_button = QPushButton("复制结果")
        self.copy_result_button.setEnabled(False)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self.copy_result_button)
        subtitle = QLabel("结果按节点名称稳定排序")
        subtitle.setObjectName("panelSubtitle")
        layout.addLayout(title_row)
        layout.addWidget(subtitle)

        cards = QGridLayout()
        cards.setSpacing(8)
        self.node_card = StatCard("节点")
        self.edge_card = StatCard("关系")
        self.order_card = StatCard("已显示")
        self.total_card = StatCard("方案总数", "-")
        self.level_card = StatCard("并行阶段", "-")
        self.state_card = StatCard("状态", "待运行")
        cards.addWidget(self.node_card, 0, 0)
        cards.addWidget(self.edge_card, 0, 1)
        cards.addWidget(self.order_card, 1, 0)
        cards.addWidget(self.total_card, 1, 1)
        cards.addWidget(self.level_card, 2, 0)
        cards.addWidget(self.state_card, 2, 1)
        layout.addLayout(cards)

        self.result_tabs = QTabWidget()
        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setPlaceholderText("运行后在此显示拓扑排序结果")
        result_page = QWidget()
        result_page_layout = QVBoxLayout(result_page)
        result_page_layout.setContentsMargins(0, 0, 0, 0)
        result_page_layout.setSpacing(6)
        result_page_layout.addWidget(self.result_editor, 1)
        pager = QHBoxLayout()
        pager.setSpacing(6)
        self.previous_page_button = QPushButton("上一页")
        self.next_page_button = QPushButton("下一页")
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setValue(1)
        self.page_spin.setFixedWidth(72)
        self.page_label = QLabel("第 1 / 1 页")
        self.result_pager = QWidget()
        self.result_pager.setLayout(pager)
        pager.addStretch()
        pager.addWidget(self.previous_page_button)
        pager.addWidget(self.page_spin)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_page_button)
        result_page_layout.addWidget(self.result_pager)
        self.result_pager.hide()
        self.insight_editor = QPlainTextEdit()
        self.insight_editor.setReadOnly(True)
        self.insight_editor.setPlaceholderText("运行后显示并行阶段、最长依赖链等智能分析")
        self.result_tabs.addTab(result_page, "排序结果")
        self.result_tabs.addTab(self.insight_editor, "智能分析")
        self.result_tabs.addTab(self._build_planner_tab(), "阶段规划")
        layout.addWidget(self.result_tabs, 1)
        return panel

    def _build_planner_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("每阶段最多"))
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 100000)
        self.capacity_spin.setValue(3)
        self.capacity_spin.setSuffix(" 项")
        self.plan_button = QPushButton("生成规划")
        self.plan_button.setEnabled(False)
        self.export_plan_button = QPushButton("导出规划")
        self.export_plan_button.setEnabled(False)
        controls.addWidget(self.capacity_spin)
        controls.addStretch()
        controls.addWidget(self.plan_button)
        controls.addWidget(self.export_plan_button)
        self.plan_editor = QPlainTextEdit()
        self.plan_editor.setReadOnly(True)
        self.plan_editor.setPlaceholderText("运行分析后，设置每阶段可安排的最大节点数，再生成规划")
        layout.addLayout(controls)
        layout.addWidget(self.plan_editor, 1)
        return page

    def _connect_signals(self) -> None:
        self.open_action.triggered.connect(self.open_file)
        self.export_result_action.triggered.connect(self.export_results)
        self.export_graph_action.triggered.connect(self.export_graph)
        self.run_action.triggered.connect(self.run_analysis)
        self.exit_action.triggered.connect(self.close)
        self.manual_action.triggered.connect(self.open_manual)
        self.about_action.triggered.connect(self.show_about)

        self.import_button.clicked.connect(self.open_file)
        self.sample_button.clicked.connect(self.load_sample)
        self.clear_button.clicked.connect(self.clear_all)
        self.export_graph_button.clicked.connect(self.export_graph)
        self.export_result_button.clicked.connect(self.export_results)
        self.run_button.clicked.connect(self.run_analysis)
        self.input_editor.textChanged.connect(self._mark_input_changed)
        self.theme_button.toggled.connect(self.toggle_theme)
        self.layout_combo.currentIndexChanged.connect(self._change_layout)
        self.reduction_check.toggled.connect(self._toggle_reduction)
        self.graph_canvas.node_selected.connect(self._show_node_details)
        self.copy_result_button.clicked.connect(self.copy_results)
        self.previous_page_button.clicked.connect(
            lambda: self.page_spin.setValue(self.page_spin.value() - 1)
        )
        self.next_page_button.clicked.connect(
            lambda: self.page_spin.setValue(self.page_spin.value() + 1)
        )
        self.page_spin.valueChanged.connect(self._show_result_page)
        self.plan_button.clicked.connect(self.run_stage_plan)
        self.export_plan_button.clicked.connect(self.export_stage_plan)
        self.capacity_spin.valueChanged.connect(self._invalidate_stage_plan)

    def _mark_input_changed(self) -> None:
        had_analysis = self._current_graph is not None or bool(self.result_editor.toPlainText())
        self._current_result = None
        self._current_graph = None
        self._invalidate_stage_plan()
        self.plan_button.setEnabled(False)
        self.result_pager.hide()
        self._set_export_enabled(False)
        self.copy_result_button.setEnabled(False)
        self.reduction_check.setChecked(False)
        self.reduction_check.setEnabled(False)
        self.status_pill.setText("待重新运行")
        if had_analysis:
            self.result_editor.setPlainText("关系数据已修改，请重新运行分析。")
            self.insight_editor.clear()
            self.graph_canvas.show_placeholder("数据已修改", "重新运行后生成最新关系图")
            self.node_detail.setText("点击图中节点，可高亮它的全部前置和后续节点")
            self._update_stats(state="待运行")

    def load_sample(self) -> None:
        self._current_file = None
        self.input_editor.setPlainText(DEFAULT_SAMPLE)
        self.input_notice.hide()
        self.statusBar().showMessage("已载入课程关系示例")

    def clear_all(self) -> None:
        self.input_editor.clear()
        self.result_editor.clear()
        self.insight_editor.clear()
        self.input_notice.hide()
        self.graph_canvas.show_placeholder()
        self._current_graph = None
        self._current_result = None
        self._current_file = None
        self._invalidate_stage_plan()
        self.plan_button.setEnabled(False)
        self.result_pager.hide()
        self._update_stats()
        self._set_export_enabled(False)
        self.copy_result_button.setEnabled(False)
        self.reduction_check.setChecked(False)
        self.reduction_check.setEnabled(False)
        self.node_detail.setText("点击图中节点，可高亮它的全部前置和后续节点")
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
        if self._active_plan_task is not None:
            return
        text = self.input_editor.toPlainText()
        parsed = parse_relations(text)

        if not parsed.is_valid:
            message = "\n".join(str(issue) for issue in parsed.errors)
            self._show_notice(message, error=True)
            self.result_editor.setPlainText("输入格式有误，请修改后重新运行。\n\n" + message)
            self.insight_editor.setPlainText("输入有效后才能生成智能分析。")
            self.graph_canvas.show_placeholder("输入格式有误", "请根据左侧提示修改关系数据")
            self._current_graph = None
            self._current_result = None
            self._invalidate_stage_plan()
            self.plan_button.setEnabled(False)
            self.result_pager.hide()
            self._update_stats(state="格式错误")
            self._set_export_enabled(False)
            self.copy_result_button.setEnabled(False)
            self.status_pill.setText("格式错误")
            self.statusBar().showMessage("输入格式错误")
            return

        assert parsed.graph is not None
        self._current_graph = parsed.graph
        self._invalidate_stage_plan()
        self.plan_button.setEnabled(False)
        self.graph_canvas.draw_graph(parsed.graph)
        self._show_notice(
            "\n".join(str(issue) for issue in parsed.warnings),
            error=False,
        )
        self._update_stats(
            parsed.graph.node_count,
            parsed.graph.edge_count,
            0,
            total="…",
            levels="…",
            state="计算中",
        )
        self.reduction_check.setChecked(False)
        self.reduction_check.setEnabled(False)
        self._set_busy(True)

        task = SolverTask(text, self.limit_spin.value())
        task.signals.finished.connect(self._on_solve_finished)
        task.signals.failed.connect(self._on_solve_failed)
        self._active_task = task
        self._thread_pool.start(task)

    def _on_solve_finished(self, result: SolveResult) -> None:
        self._current_result = result
        page_count = max(1, (result.output_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
        self.page_spin.blockSignals(True)
        self.page_spin.setRange(1, page_count)
        self.page_spin.setValue(1)
        self.page_spin.blockSignals(False)
        self.result_pager.setVisible(page_count > 1)
        self._show_result_page()

        redundant_edges = result.insights.redundant_edges if result.insights is not None else ()

        if result.has_cycle and self._current_graph is not None:
            self.graph_canvas.draw_graph(self._current_graph, result.cycle, redundant_edges)
            state = "存在环"
            self.status_pill.setText("检测到环")
        else:
            if self._current_graph is not None:
                self.graph_canvas.draw_graph(self._current_graph, (), redundant_edges)
            if result.is_complete:
                state = "已完成"
                self.status_pill.setText("全部完成")
            else:
                state = "已截断"
                self.status_pill.setText("达到上限")

        self._populate_insights(result)
        if result.insights is None:
            total: str | int = "-"
            levels: str | int = "-"
        else:
            total = (
                self._compact_number(result.insights.total_order_count)
                if result.insights.count_is_exact
                else "大规模"
            )
            levels = result.insights.level_count

        self._update_stats(
            result.node_count,
            result.edge_count,
            result.output_count,
            total,
            levels,
            state,
        )
        self._set_busy(False)
        self._set_export_enabled(True)
        self.copy_result_button.setEnabled(True)
        self.plan_button.setEnabled(result.is_successful)
        self._active_task = None
        self.statusBar().showMessage("分析完成")

    def _show_result_page(self) -> None:
        result = self._current_result
        if result is None:
            return
        page_count = self.page_spin.maximum()
        page = self.page_spin.value()
        self.page_label.setText(f"第 {page} / {page_count} 页")
        self.previous_page_button.setEnabled(page > 1)
        self.next_page_button.setEnabled(page < page_count)
        if page_count == 1:
            self.result_editor.setPlainText(format_result(result))
            return

        start = (page - 1) * RESULTS_PER_PAGE
        visible_orders = result.orders[start : start + RESULTS_PER_PAGE]
        status = "已完整枚举" if result.is_complete else "达到结果上限，未完全枚举"
        lines = [
            "拓扑排序结果",
            f"节点数：{result.node_count}  关系数：{result.edge_count}",
            f"状态：{status}",
            f"本次已生成：{result.output_count} 条；"
            f"当前显示第 {start + 1}—{start + len(visible_orders)} 条",
        ]
        if result.insights is not None and result.insights.count_is_exact:
            lines.append(f"可行顺序总数：{result.insights.total_order_count}")
        lines.append("")
        lines.extend(
            f"{index}. {' -> '.join(order)}"
            for index, order in enumerate(visible_orders, start=start + 1)
        )
        self.result_editor.setPlainText("\n".join(lines))

    def _on_solve_failed(self, message: str) -> None:
        self._set_busy(False)
        self._active_task = None
        self.status_pill.setText("运行失败")
        self.statusBar().showMessage("运行失败")
        QMessageBox.critical(self, "运行失败", message)

    def _invalidate_stage_plan(self) -> None:
        self._current_plan = None
        self.plan_editor.clear()
        self.export_plan_button.setEnabled(False)
        self.graph_canvas.set_stage_highlight(())

    def run_stage_plan(self) -> None:
        if self._current_graph is None or self._current_result is None:
            return
        if not self._current_result.is_successful or self._active_plan_task is not None:
            return
        self._invalidate_stage_plan()
        self.plan_button.setEnabled(False)
        self.capacity_spin.setEnabled(False)
        self.input_editor.setReadOnly(True)
        self.import_button.setEnabled(False)
        self.open_action.setEnabled(False)
        self.sample_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.run_action.setEnabled(False)
        self.plan_editor.setPlainText("正在计算阶段规划…")
        task = PlannerTask(self._current_graph, self.capacity_spin.value())
        task.signals.finished.connect(self._on_stage_plan_finished)
        task.signals.failed.connect(self._on_stage_plan_failed)
        self._active_plan_task = task
        self._thread_pool.start(task)

    def _on_stage_plan_finished(self, plan: StagePlanResult) -> None:
        self._active_plan_task = None
        self._current_plan = plan
        self.plan_editor.setPlainText(self._format_stage_plan(plan))
        self._finish_stage_plan_task()
        self.export_plan_button.setEnabled(plan.is_successful)
        if plan.is_successful:
            self.graph_canvas.set_stage_highlight(plan.stages)
            self.statusBar().showMessage("阶段规划已完成，关系图已按阶段着色")

    def _on_stage_plan_failed(self, message: str) -> None:
        self._active_plan_task = None
        self._finish_stage_plan_task()
        self.plan_editor.setPlainText(f"规划失败：{message}")
        self.statusBar().showMessage("阶段规划失败")

    def _finish_stage_plan_task(self) -> None:
        self.plan_button.setEnabled(self._current_result is not None)
        self.capacity_spin.setEnabled(True)
        self.input_editor.setReadOnly(False)
        self.import_button.setEnabled(True)
        self.open_action.setEnabled(True)
        self.sample_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.run_button.setEnabled(True)
        self.run_action.setEnabled(True)

    @staticmethod
    def _format_stage_plan(plan: StagePlanResult) -> str:
        if plan.errors:
            return "输入格式错误\n" + "\n".join(str(issue) for issue in plan.errors)
        if plan.cycle:
            return "存在有向环，无法规划阶段：" + " -> ".join(plan.cycle)
        method = "精确最优" if plan.is_optimal else "启发式建议（不保证最优）"
        lines = [
            "带容量限制的阶段规划",
            f"每阶段最多：{plan.capacity} 项",
            f"规划方法：{method}",
            f"阶段数：{plan.stage_count}",
            f"阶段数理论下界：{plan.lower_bound}",
            "",
        ]
        lines.extend(
            f"阶段 {index}（{len(stage)} 项）：{'、'.join(stage)}"
            for index, stage in enumerate(plan.stages, start=1)
        )
        lines.extend(
            [
                "",
                "说明：每个阶段的全部前驱必须在更早阶段完成。",
                "若节点表示课程，本规划仅考虑先修关系和数量限制，不包含学分等规则。",
            ]
        )
        return "\n".join(lines) + "\n"

    def export_stage_plan(self) -> None:
        if self._current_plan is None or not self._current_plan.is_successful:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出阶段规划", "阶段规划.txt", "文本文件 (*.txt)"
        )
        if not filename:
            return
        try:
            Path(filename).write_text(self._format_stage_plan(self._current_plan), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
            return
        self.statusBar().showMessage(f"规划已导出：{Path(filename).name}")

    def _populate_insights(self, result: SolveResult) -> None:
        insights = result.insights
        if insights is None:
            if result.has_cycle:
                self.insight_editor.setPlainText(
                    "图中存在有向环，不能生成并行阶段和学习顺序建议。\n\n"
                    f"检测到的环：{' -> '.join(result.cycle)}"
                )
            else:
                self.insight_editor.setPlainText("当前没有可用的智能分析结果。")
            self.reduction_check.setChecked(False)
            self.reduction_check.setEnabled(False)
            return

        total = (
            f"{insights.total_order_count}（精确统计）"
            if insights.count_is_exact
            else "节点数量较大，为保证响应速度未进行精确总数统计"
        )
        lines = [
            "智能分析摘要",
            "",
            f"可行顺序总数：{total}",
            f"拓扑序是否唯一：{'是' if insights.is_unique else '否'}",
            f"并行阶段数：{insights.level_count}",
            f"最大并行宽度：{insights.max_parallel_width}",
            f"最长依赖链：{' -> '.join(insights.critical_path)}",
            f"可隐藏冗余关系：{len(insights.redundant_edges)} 条",
            "",
            "分层执行建议",
        ]
        for index, level in enumerate(insights.levels, start=1):
            lines.append(f"阶段 {index}：{'、'.join(level)}")
        lines.extend(
            [
                "",
                "说明：同一阶段内的节点在依赖关系上可以并行。",
                "若节点代表课程，可把阶段作为学习批次参考，实际安排仍需结合学分等要求。",
            ]
        )
        if insights.redundant_edges:
            lines.extend(
                [
                    "",
                    "冗余关系：",
                    *(
                        f"- {source} -> {target}"
                        for source, target in insights.redundant_edges
                    ),
                ]
            )
        self.insight_editor.setPlainText("\n".join(lines))
        self.reduction_check.setEnabled(bool(insights.redundant_edges))

    def toggle_theme(self, enabled: bool) -> None:
        self._dark_mode = enabled
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(DARK_STYLESHEET if enabled else APP_STYLESHEET)
        self.theme_button.setText("浅色模式" if enabled else "深色模式")
        self.graph_canvas.set_dark_mode(enabled)
        self.statusBar().showMessage("已切换深色模式" if enabled else "已切换浅色模式")

    def _change_layout(self) -> None:
        mode = self.layout_combo.currentData()
        if isinstance(mode, str):
            self.graph_canvas.set_layout_mode(mode)
            self.statusBar().showMessage(f"已切换为{self.layout_combo.currentText()}")

    def _toggle_reduction(self, enabled: bool) -> None:
        self.graph_canvas.set_hide_redundant(enabled)
        if enabled:
            self.statusBar().showMessage("已隐藏传递冗余关系")
        else:
            self.statusBar().showMessage("已显示全部原始关系")

    def _show_node_details(self, node: str) -> None:
        if not node or self._current_graph is None:
            self.node_detail.setText("点击图中节点，可高亮它的全部前置和后续节点")
            return
        predecessors = sorted(
            source for source, target in self._current_graph.edges if target == node
        )
        successors = list(self._current_graph.adjacency[node])
        before = "、".join(predecessors) if predecessors else "无"
        after = "、".join(successors) if successors else "无"
        self.node_detail.setText(
            f"当前节点：{node}　|　直接前驱：{before}　|　直接后继：{after}"
        )

    def copy_results(self) -> None:
        if self._current_result is None:
            return
        QApplication.clipboard().setText(format_result(self._current_result))
        self.statusBar().showMessage("本次已生成的全部排序结果已复制")

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
        total: str | int = "-",
        levels: str | int = "-",
        state: str = "待运行",
    ) -> None:
        self.node_card.set_value(nodes)
        self.edge_card.set_value(edges)
        self.order_card.set_value(orders)
        self.total_card.set_value(total)
        self.level_card.set_value(levels)
        self.state_card.set_value(state)

    @staticmethod
    def _compact_number(value: int | None) -> str:
        if value is None:
            return "-"
        if value < 1_000_000:
            return f"{value:,}"
        return f"{value:.2e}"

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

    def open_manual(self) -> None:
        manual_path = Path(__file__).resolve().parents[2] / "docs" / "使用说明.md"
        if not manual_path.is_file() or not QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(manual_path))
        ):
            QMessageBox.information(
                self,
                "使用说明",
                f"请在项目文件夹中打开：\n{manual_path}",
            )
