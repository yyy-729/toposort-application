"""后台求解任务。"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from toposort_core import plan_stages, solve_text
from toposort_core.models import DirectedGraph


class SolverSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class SolverTask(QRunnable):
    def __init__(self, text: str, max_results: int) -> None:
        super().__init__()
        self.text = text
        self.max_results = max_results
        self.signals = SolverSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = solve_text(self.text, max_results=self.max_results)
        except Exception as exc:  # pragma: no cover - 最后一道后台保护
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class PlannerTask(QRunnable):
    """在后台生成带阶段容量限制的规划。"""

    def __init__(self, graph: DirectedGraph, capacity: int) -> None:
        super().__init__()
        self.graph = graph
        self.capacity = capacity
        self.signals = SolverSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = plan_stages(self.graph, self.capacity)
        except Exception as exc:  # pragma: no cover - 最后一道后台保护
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)
