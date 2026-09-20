"""支持交互高亮和多布局的关系图组件。"""

from __future__ import annotations

from math import hypot
from pathlib import Path

import matplotlib
import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from PySide6.QtCore import Signal

from toposort_core import DirectedGraph

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False


class GraphCanvas(FigureCanvasQTAgg):
    """在 Qt 中绘制并交互查看有向关系图。"""

    node_selected = Signal(str)

    def __init__(self) -> None:
        self.figure = Figure(figsize=(7.2, 5.6), dpi=100, constrained_layout=True)
        super().__init__(self.figure)
        self.setMinimumSize(420, 360)
        self._graph: DirectedGraph | None = None
        self._network = nx.DiGraph()
        self._positions: dict[str, object] = {}
        self._cycle: tuple[str, ...] = ()
        self._redundant_edges: set[tuple[str, str]] = set()
        self._selected_node = ""
        self._layout_mode = "layered"
        self._hide_redundant = False
        self._dark_mode = False
        self._has_graph = False
        self.mpl_connect("button_press_event", self._on_mouse_press)
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
                "edge": "#5B6B82",
                "unrelated": "#475569",
                "legend": "#CBD5E1",
            }
        return {
            "background": "#FFFFFF",
            "placeholder": "#56637A",
            "detail": "#8A96A8",
            "edge": "#AAB7CC",
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

    def _compute_positions(self, network: nx.DiGraph) -> dict[str, object]:
        if self._layout_mode == "circular":
            return nx.circular_layout(network)
        if self._layout_mode == "spring":
            return nx.spring_layout(network, seed=23, k=1.25)
        if self._cycle or not nx.is_directed_acyclic_graph(network):
            return nx.spring_layout(network, seed=23, k=1.25)

        generations = list(nx.topological_generations(network))
        layers = {
            node: layer
            for layer, generation in enumerate(generations)
            for node in sorted(generation)
        }
        nx.set_node_attributes(network, layers, "layer")
        return nx.multipartite_layout(network, subset_key="layer", align="vertical")

    def _node_colors(self, network: nx.DiGraph) -> list[str]:
        cycle_nodes = set(self._cycle)
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

        colors = []
        for node in network.nodes:
            if node in cycle_nodes:
                colors.append("#E5484D")
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
        if self._selected_node:
            return [
                Patch(facecolor="#00A6C7", label="当前节点"),
                Patch(facecolor="#3157D5", label="所有前置"),
                Patch(facecolor="#22A06B", label="所有后续"),
                Patch(facecolor=self._colors()["unrelated"], label="其他"),
            ]
        items = [
            Patch(facecolor="#3157D5", label="起点"),
            Patch(facecolor="#7457C8", label="中间节点"),
            Patch(facecolor="#E9952F", label="终点"),
        ]
        if self._cycle:
            items.append(Patch(facecolor="#E5484D", label="环路节点"))
        return items

    def _render(self) -> None:
        assert self._graph is not None
        colors = self._colors()
        network = self._build_network()
        positions = self._compute_positions(network)

        self.figure.clear()
        self.figure.patch.set_facecolor(colors["background"])
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(colors["background"])
        axis.axis("off")

        edge_colors, edge_widths = self._edge_style(network)
        if self._graph.node_count >= 13:
            minimum_size, maximum_size, character_factor = 1200, 3000, 48
        elif self._graph.node_count >= 8:
            minimum_size, maximum_size, character_factor = 1550, 4600, 65
        else:
            minimum_size, maximum_size, character_factor = 1900, 8200, 85
        node_sizes = [
            min(
                maximum_size,
                max(minimum_size, 800 + len(node) * len(node) * character_factor),
            )
            for node in network.nodes
        ]
        font_size = 8 if self._graph.node_count > 24 else 9

        nx.draw_networkx_nodes(
            network,
            positions,
            ax=axis,
            node_color=self._node_colors(network),
            node_size=node_sizes,
            edgecolors=colors["background"],
            linewidths=2.0,
            alpha=0.97,
        )
        nx.draw_networkx_edges(
            network,
            positions,
            ax=axis,
            edge_color=edge_colors,
            width=edge_widths,
            arrows=True,
            arrowsize=17,
            arrowstyle="-|>",
            connectionstyle="arc3,rad=0.035",
            min_source_margin=25,
            min_target_margin=25,
        )
        nx.draw_networkx_labels(
            network,
            positions,
            ax=axis,
            font_size=font_size,
            font_color="#FFFFFF",
            font_weight="bold",
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
        axis.margins(0.18)
        self._network = network
        self._positions = positions
        self._has_graph = True
        self.draw_idle()

    def _on_mouse_press(self, event: object) -> None:
        if not self._has_graph or getattr(event, "inaxes", None) is None:
            return
        click_x = getattr(event, "x", None)
        click_y = getattr(event, "y", None)
        if click_x is None or click_y is None:
            return

        axis = event.inaxes
        closest = ""
        closest_distance = 50.0
        for node, position in self._positions.items():
            display_x, display_y = axis.transData.transform(position)
            distance = hypot(display_x - click_x, display_y - click_y)
            if distance < closest_distance:
                closest = node
                closest_distance = distance

        if not closest:
            return
        self._selected_node = "" if closest == self._selected_node else closest
        self._render()
        self.node_selected.emit(self._selected_node)

    def export(self, path: str | Path) -> None:
        if not self._has_graph:
            raise ValueError("当前没有可导出的关系图")
        self.figure.savefig(
            path,
            dpi=220,
            facecolor=self._colors()["background"],
            bbox_inches="tight",
        )
