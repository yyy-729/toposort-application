"""支持自适应布局、交互高亮和高清导出的关系图组件。"""

from __future__ import annotations

from math import hypot, inf
from pathlib import Path
from unicodedata import east_asian_width

import matplotlib
import networkx as nx
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Patch
from matplotlib.text import Text
from matplotlib.transforms import Bbox
from PySide6.QtCore import Signal

from toposort_core import DirectedGraph

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False


def _character_width(character: str) -> int:
    return 2 if east_asian_width(character) in {"F", "W"} else 1


def _wrap_label(value: str, *, line_width: int, max_lines: int | None) -> str:
    """按中英文视觉宽度换行；预览超长名称时以省略号表示。"""
    lines: list[str] = []
    current = ""
    width = 0
    for character in value:
        character_width = _character_width(character)
        if current and width + character_width > line_width:
            lines.append(current)
            current = ""
            width = 0
        current += character
        width += character_width
    if current:
        lines.append(current)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and sum(_character_width(char) for char in last) + 1 > line_width:
            last = last[:-1]
        lines[-1] = last + "…"
    return "\n".join(lines)


def _boundary_fraction(box: Bbox, delta_x: float, delta_y: float, length: float) -> float:
    x_fraction = (box.width / 2) / abs(delta_x) if delta_x else inf
    y_fraction = (box.height / 2) / abs(delta_y) if delta_y else inf
    return min(x_fraction, y_fraction) + 10 / length


class GraphCanvas(FigureCanvasQTAgg):
    """在 Qt 中绘制并交互查看有向关系图。"""

    node_selected = Signal(str)

    def __init__(self) -> None:
        self.figure = Figure(figsize=(7.2, 5.6), dpi=100)
        super().__init__(self.figure)
        self.setMinimumSize(420, 360)
        self._graph: DirectedGraph | None = None
        self._network = nx.DiGraph()
        self._positions: dict[str, object] = {}
        self._node_artists: dict[str, Text] = {}
        self._cycle: tuple[str, ...] = ()
        self._redundant_edges: set[tuple[str, str]] = set()
        self._selected_node = ""
        self._layout_mode = "layered"
        self._hide_redundant = False
        self._dark_mode = False
        self._has_graph = False
        self._stage_lookup: dict[str, int] = {}
        self._trace_candidates: set[str] = set()
        self._trace_selected = ""
        self._trace_completed: set[str] = set()
        self.mpl_connect("button_press_event", self._on_mouse_press)
        self.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.show_placeholder()

    @property
    def has_graph(self) -> bool:
        return self._has_graph

    @property
    def selected_node(self) -> str:
        return self._selected_node

    def _colors(self) -> dict[str, str]:
        if self._dark_mode:
            return {
                "background": "#111827",
                "placeholder": "#94A3B8",
                "detail": "#64748B",
                "edge": "#667790",
                "unrelated": "#475569",
                "legend": "#CBD5E1",
            }
        return {
            "background": "#FFFFFF",
            "placeholder": "#56637A",
            "detail": "#8A96A8",
            "edge": "#8294B1",
            "unrelated": "#A8B2C1",
            "legend": "#334155",
        }

    def show_placeholder(
        self,
        title: str = "等待生成关系图",
        detail: str = "输入关系数据后，点击“运行分析”",
    ) -> None:
        colors = self._colors()
        self.figure.clear()
        self.figure.patch.set_facecolor(colors["background"])
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(colors["background"])
        axis.axis("off")
        axis.text(
            0.5,
            0.54,
            "↗",
            ha="center",
            va="center",
            fontsize=42,
            color="#B7C3D8" if not self._dark_mode else "#475569",
            transform=axis.transAxes,
        )
        axis.text(
            0.5,
            0.40,
            title,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            color=colors["placeholder"],
            transform=axis.transAxes,
        )
        axis.text(
            0.5,
            0.33,
            detail,
            ha="center",
            va="center",
            fontsize=10,
            color=colors["detail"],
            transform=axis.transAxes,
        )
        self._has_graph = False
        self._selected_node = ""
        self._graph = None
        self._network = nx.DiGraph()
        self._positions = {}
        self._node_artists = {}
        self._cycle = ()
        self._redundant_edges = set()
        self._stage_lookup = {}
        self._trace_candidates = set()
        self._trace_selected = ""
        self._trace_completed = set()
        self.draw_idle()

    def draw_graph(
        self,
        graph: DirectedGraph,
        cycle: tuple[str, ...] = (),
        redundant_edges: tuple[tuple[str, str], ...] = (),
    ) -> None:
        self._graph = graph
        self._cycle = cycle
        self._redundant_edges = set(redundant_edges)
        self._selected_node = ""
        self._stage_lookup = {}
        self._trace_candidates = set()
        self._trace_selected = ""
        self._trace_completed = set()
        self._render()

    def set_layout_mode(self, mode: str) -> None:
        if mode not in {"layered", "spring", "circular"}:
            raise ValueError(f"不支持的布局：{mode}")
        self._layout_mode = mode
        if self._graph is not None:
            self._render()

    def set_hide_redundant(self, enabled: bool) -> None:
        self._hide_redundant = enabled
        if self._graph is not None:
            self._render()

    def set_dark_mode(self, enabled: bool) -> None:
        self._dark_mode = enabled
        if self._graph is None:
            self.show_placeholder()
        else:
            self._render()

    def set_stage_highlight(self, stages: tuple[tuple[str, ...], ...] | None) -> None:
        """按阶段着色节点；传入 None 可恢复原有的起点/终点着色。"""
        self._stage_lookup = {
            node: index for index, stage in enumerate(stages or ()) for node in stage
        }
        if self._graph is not None:
            self._render()

    def set_trace_highlight(
        self,
        candidates: tuple[str, ...] = (),
        selected: str = "",
        completed: tuple[str, ...] = (),
    ) -> None:
        """为算法回放着色，空参数恢复原有节点颜色。"""
        self._trace_candidates = set(candidates)
        self._trace_selected = selected
        self._trace_completed = set(completed)
        if candidates or selected or completed:
            self._selected_node = ""
        if self._graph is not None:
            self._render()

    def _build_network(self) -> nx.DiGraph:
        assert self._graph is not None
        network = nx.DiGraph()
        network.add_nodes_from(self._graph.nodes)
        network.add_edges_from(
            edge
            for edge in self._graph.edges
            if not (self._hide_redundant and edge in self._redundant_edges)
        )
        return network

    @staticmethod
    def _is_simple_chain(network: nx.DiGraph) -> bool:
        return (
            len(network) > 10
            and network.number_of_edges() == len(network) - 1
            and nx.is_weakly_connected(network)
            and all(
                network.in_degree(node) <= 1 and network.out_degree(node) <= 1
                for node in network
            )
        )

    def _compute_positions(self, network: nx.DiGraph) -> dict[str, tuple[float, float]]:
        if self._layout_mode == "circular":
            return nx.circular_layout(network)
        if self._layout_mode == "spring":
            return nx.spring_layout(network, seed=23, k=1.25)
        if self._cycle or not nx.is_directed_acyclic_graph(network):
            return nx.spring_layout(network, seed=23, k=1.25)

        if self._is_simple_chain(network):
            # 长链折行为蛇形，避免几十个节点被压成一条不可读的直线。
            columns = 6
            ordered = list(nx.topological_sort(network))
            positions = {}
            for index, node in enumerate(ordered):
                row, column = divmod(index, columns)
                if row % 2:
                    column = columns - 1 - column
                positions[node] = (float(column), float(-row))
            return positions

        # 先按拓扑层划分，再按前驱重心排序，减少图 1 一类数据的交叉。
        generations = [sorted(generation) for generation in nx.topological_generations(network)]
        positions = {}
        for layer, generation in enumerate(generations):
            if layer:
                generation.sort(
                    key=lambda node: (
                        sum(positions[parent][1] for parent in network.predecessors(node))
                        / max(network.in_degree(node), 1),
                        node,
                    ),
                    reverse=True,
                )
            for row, node in enumerate(generation):
                positions[node] = (float(layer), (len(generation) - 1) / 2 - row)
        return positions

    def _node_colors(self, network: nx.DiGraph) -> list[str]:
        cycle_nodes = set(self._cycle)
        if self._trace_candidates or self._trace_selected or self._trace_completed:
            colors = []
            for node in network.nodes:
                if node in cycle_nodes or node == self._trace_selected:
                    colors.append("#E5484D")
                elif node in self._trace_candidates:
                    colors.append("#22A06B")
                elif node in self._trace_completed:
                    colors.append("#3157D5")
                else:
                    colors.append(self._colors()["unrelated"])
            return colors
        if self._selected_node:
            ancestors = nx.ancestors(network, self._selected_node)
            descendants = nx.descendants(network, self._selected_node)
            colors = []
            for node in network.nodes:
                if node == self._selected_node:
                    colors.append("#00A6C7")
                elif node in cycle_nodes:
                    colors.append("#E5484D")
                elif node in ancestors:
                    colors.append("#3157D5")
                elif node in descendants:
                    colors.append("#22A06B")
                else:
                    colors.append(self._colors()["unrelated"])
            return colors

        palette = ("#3157D5", "#7457C8", "#D88727", "#168A76", "#9C477C")
        colors = []
        for node in network.nodes:
            if node in cycle_nodes:
                colors.append("#E5484D")
            elif node in self._stage_lookup:
                colors.append(palette[self._stage_lookup[node] % len(palette)])
            elif network.in_degree(node) == 0:
                colors.append("#3157D5")
            elif network.out_degree(node) == 0:
                colors.append("#E9952F")
            else:
                colors.append("#7457C8")
        return colors

    def _edge_style(self, network: nx.DiGraph) -> tuple[list[str], list[float]]:
        cycle_edges = set(zip(self._cycle[:-1], self._cycle[1:], strict=True))
        colors: list[str] = []
        widths: list[float] = []
        for source, target in network.edges:
            if (source, target) in cycle_edges:
                colors.append("#E5484D")
                widths.append(2.8)
            elif self._selected_node and target == self._selected_node:
                colors.append("#3157D5")
                widths.append(2.5)
            elif self._selected_node and source == self._selected_node:
                colors.append("#22A06B")
                widths.append(2.5)
            else:
                colors.append(self._colors()["edge"])
                widths.append(1.6)
        return colors, widths

    def _legend_items(self) -> list[Patch]:
        if self._trace_candidates or self._trace_selected or self._trace_completed:
            return [
                Patch(facecolor="#3157D5", label="已完成"),
                Patch(facecolor="#22A06B", label="当前可选"),
                Patch(facecolor="#E5484D", label="本步选择"),
            ]
        if self._selected_node:
            return [
                Patch(facecolor="#00A6C7", label="当前节点"),
                Patch(facecolor="#3157D5", label="所有前置"),
                Patch(facecolor="#22A06B", label="所有后续"),
                Patch(facecolor=self._colors()["unrelated"], label="其他"),
            ]
        if self._stage_lookup:
            return [Patch(facecolor="#3157D5", label="阶段颜色循环显示")]
        items = [
            Patch(facecolor="#3157D5", label="起点"),
            Patch(facecolor="#7457C8", label="中间节点"),
            Patch(facecolor="#E9952F", label="终点"),
        ]
        if self._cycle:
            items.append(Patch(facecolor="#E5484D", label="环路节点"))
        return items

    def _draw_on_figure(self, figure: Figure, *, export: bool) -> None:
        assert self._graph is not None
        colors = self._colors()
        network = self._build_network()
        positions = self._compute_positions(network)
        figure.clear()
        figure.patch.set_facecolor(colors["background"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(colors["background"])
        axis.axis("off")
        x_values = [position[0] for position in positions.values()]
        y_values = [position[1] for position in positions.values()]
        axis.set_xlim(min(x_values) - 0.6, max(x_values) + 0.6)
        axis.set_ylim(min(y_values) - 0.6, max(y_values) + 0.6)
        axis.set_autoscale_on(False)

        count = self._graph.node_count
        if export:
            line_width = 28 if count <= 20 else 20
            max_lines = None
            font_size = 10 if count <= 20 else 8
        else:
            line_width = 24 if count <= 5 else 16 if count <= 20 else 12
            max_lines = 3 if count <= 5 else 2
            font_size = 9 if count <= 20 else 7
        node_artists = {}
        for node, facecolor in zip(network.nodes, self._node_colors(network), strict=True):
            x, y = positions[node]
            node_artists[node] = axis.text(
                x,
                y,
                _wrap_label(node, line_width=line_width, max_lines=max_lines),
                ha="center",
                va="center",
                fontsize=font_size,
                fontweight="bold",
                color="#FFFFFF",
                linespacing=1.2,
                zorder=3,
                bbox={
                    "boxstyle": "round,pad=0.48,rounding_size=0.23",
                    "facecolor": facecolor,
                    "edgecolor": colors["background"],
                    "linewidth": 1.5,
                    "alpha": 0.98,
                },
            )

        # 文字节点的外框尺寸由实际字体决定，先测量像素边界，再让箭头在外框前停止。
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        bounds = {
            node: artist.get_window_extent(renderer=renderer)
            for node, artist in node_artists.items()
        }
        edge_colors, edge_widths = self._edge_style(network)
        for (source, target), edge_color, edge_width in zip(
            network.edges, edge_colors, edge_widths, strict=True
        ):
            if source == target:
                nx.draw_networkx_edges(
                    network,
                    positions,
                    edgelist=[(source, target)],
                    ax=axis,
                    edge_color=edge_color,
                    width=edge_width,
                    arrows=True,
                    arrowsize=16 if export else 13,
                    node_size=900,
                )
                continue
            source_px = axis.transData.transform(positions[source])
            target_px = axis.transData.transform(positions[target])
            delta_x = target_px[0] - source_px[0]
            delta_y = target_px[1] - source_px[1]
            length = hypot(delta_x, delta_y)
            if length == 0:
                continue

            start_fraction = _boundary_fraction(bounds[source], delta_x, delta_y, length)
            end_fraction = _boundary_fraction(bounds[target], delta_x, delta_y, length)
            if start_fraction + end_fraction >= 0.96:
                continue
            start_px = source_px + (target_px - source_px) * start_fraction
            end_px = target_px - (target_px - source_px) * end_fraction
            axis.add_patch(
                FancyArrowPatch(
                    axis.transData.inverted().transform(start_px),
                    axis.transData.inverted().transform(end_px),
                    arrowstyle="-|>,head_length=0.7,head_width=0.4",
                    mutation_scale=17 if export else 14,
                    linewidth=edge_width,
                    color=edge_color,
                    shrinkA=0,
                    shrinkB=0,
                    zorder=2,
                )
            )

        legend_items = self._legend_items()
        legend = axis.legend(
            handles=legend_items,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.015),
            ncol=len(legend_items),
            frameon=False,
            fontsize=9,
        )
        for label in legend.get_texts():
            label.set_color(colors["legend"])
        if not export:
            self._network = network
            self._positions = positions
            self._node_artists = node_artists
            self._has_graph = True

    def _render(self) -> None:
        self._draw_on_figure(self.figure, export=False)
        self.draw_idle()

    def _closest_node(self, event: object, *, radius: float = 50.0) -> str:
        if not self._has_graph or getattr(event, "inaxes", None) is None:
            return ""
        click_x = getattr(event, "x", None)
        click_y = getattr(event, "y", None)
        if click_x is None or click_y is None:
            return ""
        axis = event.inaxes
        renderer = self.figure.canvas.get_renderer()
        for node, artist in self._node_artists.items():
            if artist.get_window_extent(renderer=renderer).contains(click_x, click_y):
                return node
        closest = ""
        closest_distance = radius
        for node, position in self._positions.items():
            display_x, display_y = axis.transData.transform(position)
            distance = hypot(display_x - click_x, display_y - click_y)
            if distance < closest_distance:
                closest = node
                closest_distance = distance
        return closest

    def _on_mouse_press(self, event: object) -> None:
        if self._trace_candidates or self._trace_selected or self._trace_completed:
            return
        closest = self._closest_node(event)
        if not closest:
            return
        self._selected_node = "" if closest == self._selected_node else closest
        self._render()
        self.node_selected.emit(self._selected_node)

    def _on_mouse_move(self, event: object) -> None:
        self.setToolTip(self._closest_node(event))

    def export(self, path: str | Path) -> None:
        if not self._has_graph:
            raise ValueError("当前没有可导出的关系图")
        x_values = [position[0] for position in self._positions.values()]
        y_values = [position[1] for position in self._positions.values()]
        width = min(24.0, max(8.0, 2.2 * (max(x_values) - min(x_values) + 1)))
        height = min(18.0, max(6.0, 1.55 * (max(y_values) - min(y_values) + 1)))
        if self._graph is not None and any(len(node) > 20 for node in self._graph.nodes):
            width = min(24.0, max(width, 12.0))
        export_figure = Figure(figsize=(width, height), dpi=100)
        FigureCanvasAgg(export_figure)
        self._draw_on_figure(export_figure, export=True)
        export_figure.savefig(
            path,
            dpi=180,
            facecolor=self._colors()["background"],
            bbox_inches="tight",
        )
