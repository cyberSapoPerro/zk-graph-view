import tempfile
import webbrowser

import colorir as cl
import numpy as np
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional


def make_interactive_graph(
    data,
    palette,
    output_path=None
):
    net = Network(
        height="100vh",
        width="100%",
        directed=True,
        cdn_resources="remote"
    )

    # --- Tags ---
    tags = [
        note["tags"][0] if note["tags"] else "untagged" for note in data["notes"]
    ]

    # -- Color map ---
    palette = cl.StackPalette.load(
        palette,
        palettes_dir=cl.config.USR_PALETTES_DIR
    ).resize(len(tags))
    color_map = {tag: color for tag, color in zip(tags, palette)}
    color_map["untagged"] = cl.Hex("#808080")


    # -- Nodes size ---
    backlinks = {}
    for note in data["notes"]:
        note_id = note["filenameStem"]
        n_backlinks = 0
        for link in data["links"]:
            target = link["targetPath"].replace(".md", "")
            if note_id == target:
                n_backlinks += 1
        backlinks[note_id] = n_backlinks

    # --- Nodes ---
    for note in data["notes"]:
        node_id = note["filenameStem"]  # unique ID
        label = note["title"]
        if note["tags"]:
            tag = note["tags"][0]
        else:
            tag = "untagged"
        net.add_node(
            node_id,
            label=label,
            color=color_map[tag],
            size= 10 + 10 * np.log(backlinks[node_id] + 1),
            shape="dot"
        )

    # --- Edges ---
    for link in data["links"]:
        source = link["sourcePath"].replace(".md", "")
        target = link["targetPath"].replace(".md", "")
        net.add_edge(source, target)

    # --- Open the graph ---
    if output_path is None:
        with tempfile.NamedTemporaryFile(suffix=".html") as f:
            html_path = f.name
    else:
        html_path = output_path
    net.write_html(html_path)

    def build_legend_html(color_map):
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

    # -- Make the lengend ---
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
    output_path: Optional[str] = None,
    layout: str = "auto",
    label_mode: str = "pagerank",
    top_k: int = 50,
    size_threshold: float = 25.0,
) -> None:
    """
    Render a static directed note graph using NetworkX and Matplotlib.

    This function builds a graph from note/link data, assigns node colors based on tags,
    scales node sizes using backlink counts, and applies a layout strategy optimized
    for medium-to-large graphs (~3k nodes). Labels are selectively rendered to avoid
    visual clutter, using either PageRank or node size as a ranking heuristic.

    Args:
        data: Dictionary containing:
            - "notes": list of note objects with keys:
                - "filenameStem": unique node identifier
                - "title": display label
                - "tags": list of tags (optional)
            - "links": list of link objects with keys:
                - "sourcePath": source note path (".md" suffix expected)
                - "targetPath": target note path (".md" suffix expected)
        palette: Name of a Colorir palette to use for tag-based coloring.
        output_path: If provided, saves the graph as an image at this path;
            otherwise displays it interactively.
        layout: Layout algorithm to use:
            - "auto": Kamada–Kawai for small graphs, spring layout otherwise
            - "kamada_kawai": force Kamada–Kawai layout
            - "spring": force Fruchterman–Reingold layout
        label_mode: Strategy for selecting labeled nodes:
            - "pagerank": label top-k nodes by PageRank
            - "size": label nodes above a size threshold
        top_k: Number of top-ranked nodes to label when using "pagerank".
        size_threshold: Minimum node size required for labeling when using "size".

    Returns:
        None
    """
    G = nx.DiGraph()

    tags = [
        note["tags"][0] if note["tags"] else "untagged"
        for note in data["notes"]
    ]
    unique_tags = list(set(tags))

    palette_obj = cl.StackPalette.load(
        palette,
        palettes_dir=cl.config.USR_PALETTES_DIR
    ).resize(len(unique_tags))

    color_map = {tag: color.hex for tag, color in zip(unique_tags, palette_obj)}
    color_map["untagged"] = "#808080"

    backlinks: Dict[str, int] = {}
    for note in data["notes"]:
        note_id = note["filenameStem"]
        backlinks[note_id] = sum(
            1
            for link in data["links"]
            if note_id == link["targetPath"].replace(".md", "")
        )

    for note in data["notes"]:
        node_id = note["filenameStem"]
        label = note["title"]
        tag = note["tags"][0] if note["tags"] else "untagged"

        G.add_node(
            node_id,
            label=label,
            color=color_map[tag],
            size=10 + 10 * np.log(backlinks[node_id] + 1)
        )

    for link in data["links"]:
        source = link["sourcePath"].replace(".md", "")
        target = link["targetPath"].replace(".md", "")
        G.add_edge(source, target)

    if layout == "auto":
        if len(G) < 1500:
            try:
                pos = nx.kamada_kawai_layout(G)
            except Exception:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    else:
        raise ValueError(f"Unknown layout: {layout}")

    node_colors = [G.nodes[n]["color"] for n in G.nodes]
    node_sizes = [G.nodes[n]["size"] * 20 for n in G.nodes]

    if label_mode == "pagerank":
        pagerank = nx.pagerank(G, alpha=0.85)
        top_nodes = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        selected = {node for node, _ in top_nodes}
        labels = {
            n: G.nodes[n]["label"]
            for n in G.nodes
            if n in selected
        }
    elif label_mode == "size":
        labels = {
            n: G.nodes[n]["label"]
            for n in G.nodes
            if G.nodes[n]["size"] > size_threshold
        }
    else:
        raise ValueError(f"Unknown label_mode: {label_mode}")

    plt.figure(figsize=(14, 12))

    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes
    )

    nx.draw_networkx_edges(
        G, pos,
        arrows=True,
        arrowstyle="->",
        arrowsize=8,
        alpha=0.4
    )

    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=9,
        font_weight="bold"
    )

    for tag, color in color_map.items():
        plt.scatter([], [], c=color, label=tag)
    plt.legend(title="Tags", loc="best")

    plt.axis("off")

    if output_path:
        plt.savefig(output_path, bbox_inches="tight", dpi=300)
    else:
        plt.show()
