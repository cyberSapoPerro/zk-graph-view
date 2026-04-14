from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from ._graph_shared import build_color_map
from ..api import transform_json_data


def should_render_legend(unique_tags: List[str]) -> bool:
    """Return True when there is at least one tag other than untagged."""
    return any(tag != "untagged" for tag in unique_tags)


def make_static_graph(
    data: Dict[str, Any],
    palette: str,
    layout: Dict[str, tuple[float, float]],
    output_path: Optional[str] = None,
) -> None:
    """Render a static note graph using a pre-computed layout.

    Uses the transformed data to build a directed graph and renders it
    with matplotlib using the provided node positions.

    Args:
        data: Raw graph data with ``notes`` and ``links`` keys.
        palette: Name of a Colorir palette to use for tag-based coloring.
        layout: Dict mapping node IDs to (x, y) position tuples.
        output_path: Path to save the graph image. Required.
    """
    if not output_path:
        raise ValueError("output_path is required for static graph")

    data = transform_json_data(data)

    graph = nx.DiGraph()

    unique_tags: List[str] = list({note["tag"] for note in data["notes"]})
    color_map = build_color_map(unique_tags, palette)
    render_legend = should_render_legend(unique_tags)

    for note in data["notes"]:
        graph.add_node(
            note["filenameStem"],
            label=note["title"],
            size=10 + 10 * np.log(note["backlinks"] + 1),
        )

    for link in data["links"]:
        graph.add_edge(link["sourcePath"], link["targetPath"])

    node_colors = [str(color_map[note["tag"]]) for note in data["notes"]]
    node_sizes = [
        (10 + 10 * np.log(note["backlinks"] + 1)) * 20 for note in data["notes"]
    ]

    plt.figure(figsize=(14, 12))

    nx.draw_networkx_nodes(graph, layout, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(
        graph, layout, arrows=True, arrowstyle="->", arrowsize=8, alpha=0.4
    )

    if render_legend:
        for tag, color in color_map.items():
            plt.scatter([], [], c=str(color), label=tag)
        plt.legend(title="Tags", loc="best")

    plt.axis("off")

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
