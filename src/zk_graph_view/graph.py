import tempfile
import webbrowser

import colorir as cl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pyvis.network import Network

from .api import transform_json_data
from typing import Any, Dict, List, Optional


def build_color_map(unique_tags: List[str], palette: str) -> Dict[str, cl.Hex]:
    """Build a color map from a list of tags and a palette name.

    Args:
        unique_tags: List of unique tag names.
        palette: Name of a Colorir palette to use for coloring.

    Returns:
        Dict mapping each tag to a Hex color, including "untagged" as gray.
    """
    palette_obj = cl.StackPalette.load(
        palette, palettes_dir=cl.config.USR_PALETTES_DIR
    ).resize(len(unique_tags))
    color_map = {tag: color for tag, color in zip(unique_tags, palette_obj)}
    color_map["untagged"] = cl.Hex("#808080")
    return color_map


def make_interactive_graph(
    data: Dict[str, Any],
    palette: str,
    output_path: Optional[str] = None,
) -> None:
    """Render an interactive note graph using Pyvis.

    Transforms raw zk graph data, then builds a directed graph with nodes
    colored by tag and sized by backlink count.

    Args:
        data: Raw graph data with ``notes`` and ``links`` keys.
        palette: Name of a Colorir palette to use for tag-based coloring.
        output_path: If provided, saves the graph at this path; otherwise
            uses a temporary file.

    Returns:
        None
    """
    data = transform_json_data(data)

    net = Network(height="100vh", width="100%", directed=True, cdn_resources="remote")

    unique_tags: List[str] = list({note["tag"] for note in data["notes"]})
    color_map = build_color_map(unique_tags, palette)

    for note in data["notes"]:
        net.add_node(
            note["filenameStem"],
            label=note["title"],
            color=color_map[note["tag"]],
            size=10 + 10 * np.log(note["backlinks"] + 1),
            shape="dot",
        )

    for link in data["links"]:
        net.add_edge(link["sourcePath"], link["targetPath"])

    if output_path is None:
        with tempfile.NamedTemporaryFile(suffix=".html") as f:
            html_path = f.name
    else:
        html_path = output_path
    net.write_html(html_path)

    def build_legend_html(color_map: Dict[str, cl.Hex]) -> str:
        rows = ""
        for tag, color in color_map.items():
            rows += f"""
            <tr>
                <td style="padding: 4px;">
                    <div style="
                        width: 15px;
                        height: 15px;
                        background-color: {color};
                        border-radius: 3px;
                    "></div>
                </td>
                <td style="padding: 4px;">{tag}</td>
            </tr>
            """

        legend = f"""
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            z-index: 9999;
            font-family: sans-serif;
            font-size: 14px;
        ">
            <b>Tags</b>
            <table>
                {rows}
            </table>
        </div>
        """
        return legend

    legend_html = build_legend_html(color_map)
    with open(html_path, "r+") as f:
        html = f.read()
        html = html.replace("</body>", legend_html + "\n</body>")
        f.seek(0)
        f.write(html)
        f.truncate()

    webbrowser.open(f"file://{html_path}")


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

    Returns:
        None. Saves the graph to ``output_path``.
    """
    if not output_path:
        raise ValueError("output_path is required for static graph")

    data = transform_json_data(data)

    G = nx.DiGraph()

    unique_tags: List[str] = list({note["tag"] for note in data["notes"]})
    color_map = build_color_map(unique_tags, palette)

    for note in data["notes"]:
        G.add_node(
            note["filenameStem"],
            label=note["title"],
            size=10 + 10 * np.log(note["backlinks"] + 1),
        )

    for link in data["links"]:
        G.add_edge(link["sourcePath"], link["targetPath"])

    node_colors = [str(color_map[note["tag"]]) for note in data["notes"]]
    node_sizes = [
        (10 + 10 * np.log(note["backlinks"] + 1)) * 20 for note in data["notes"]
    ]

    plt.figure(figsize=(14, 12))

    nx.draw_networkx_nodes(G, layout, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(
        G, layout, arrows=True, arrowstyle="->", arrowsize=8, alpha=0.4
    )

    for tag, color in color_map.items():
        plt.scatter([], [], c=str(color), label=tag)
    plt.legend(title="Tags", loc="best")

    plt.axis("off")

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
