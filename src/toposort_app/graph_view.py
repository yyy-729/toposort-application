"""关系图显示组件。"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from toposort_core import DirectedGraph

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False


class GraphCanvas(FigureCanvasQTAgg):
    """在 Qt 中显示有向关系图。"""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(7.2, 5.6), dpi=100, constrained_layout=True)
        self.figure.patch.set_facecolor("#FFFFFF")
        super().__init__(self.figure)
        self.setMinimumSize(420, 360)
        self._has_graph = False
        self.show_placeholder()

    @property
    def has_graph(self) -> bool:
        return self._has_graph

    def show_placeholder(
        self,
        title: str = "等待生成关系图",
        detail: str = "输入关系数据后，点击“运行分析”",
    ) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_facecolor("#FFFFFF")
        axis.axis("off")
        axis.text(
            0.5,
            0.54,
            "↗",
            ha="center",
            va="center",
            fontsize=42,
            color="#B7C3D8",
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
            color="#56637A",
            transform=axis.transAxes,
        )
        axis.text(
            0.5,
            0.33,
            detail,
            ha="center",
            va="center",
            fontsize=10,
            color="#8A96A8",
            transform=axis.transAxes,
        )
        self._has_graph = False
        self.draw_idle()

    def draw_graph(self, graph: DirectedGraph, cycle: tuple[str, ...] = ()) -> None:
        network = nx.DiGraph()
        network.add_nodes_from(graph.nodes)
        network.add_edges_from(graph.edges)

        cycle_edges = set(zip(cycle[:-1], cycle[1:], strict=True)) if cycle else set()
        if cycle or not nx.is_directed_acyclic_graph(network):
            positions = nx.spring_layout(network, seed=23, k=1.25)
        else:
            generations = list(nx.topological_generations(network))
            layers = {
                node: layer
                for layer, generation in enumerate(generations)
                for node in sorted(generation)
            }
            nx.set_node_attributes(network, layers, "layer")
            positions = nx.multipartite_layout(network, subset_key="layer", align="vertical")

        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_facecolor("#FFFFFF")
        axis.axis("off")

        cycle_nodes = set(cycle)
        node_colors: list[str] = []
        for node in network.nodes:
            if node in cycle_nodes:
                node_colors.append("#E5484D")
            elif network.in_degree(node) == 0:
                node_colors.append("#3157D5")
            elif network.out_degree(node) == 0:
                node_colors.append("#E9952F")
            else:
                node_colors.append("#7457C8")

        edge_colors = ["#E5484D" if edge in cycle_edges else "#AAB7CC" for edge in network.edges]
        edge_widths = [2.8 if edge in cycle_edges else 1.6 for edge in network.edges]
        node_sizes = [
            min(8200, max(1900, 800 + len(node) * len(node) * 85)) for node in network.nodes
        ]
        font_size = 8 if graph.node_count > 24 else 9

        nx.draw_networkx_nodes(
            network,
            positions,
            ax=axis,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors="#FFFFFF",
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

        legend_items = [
            Patch(facecolor="#3157D5", label="起点"),
            Patch(facecolor="#7457C8", label="中间节点"),
            Patch(facecolor="#E9952F", label="终点"),
        ]
        if cycle:
            legend_items.append(Patch(facecolor="#E5484D", label="环路节点"))
        axis.legend(
            handles=legend_items,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.015),
            ncol=len(legend_items),
            frameon=False,
            fontsize=9,
        )
        axis.margins(0.18)
        self._has_graph = True
        self.draw_idle()

    def export(self, path: str | Path) -> None:
        if not self._has_graph:
            raise ValueError("当前没有可导出的关系图")
        self.figure.savefig(path, dpi=220, facecolor="#FFFFFF", bbox_inches="tight")
