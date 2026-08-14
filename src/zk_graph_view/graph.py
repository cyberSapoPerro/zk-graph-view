"""Graph generation and visualization for zettelkasten notes."""

import tempfile
import warnings
import webbrowser
from typing import Any, Dict, List, Optional

import colorir as cl
import numpy as np
from pyvis.network import Network

from .api import transform_json_data

def build_color_map(unique_tags: List[str], palette: str) -> Dict[str, cl.Hex]:
    """Build a color map from a list of tags and a palette name."""
    palette_obj = cl.StackPalette.load(
        palette, palettes_dir=cl.config.USR_PALETTES_DIR
    ).resize(len(unique_tags))
    color_map = {tag: color for tag, color in zip(unique_tags, palette_obj)}
    color_map["untagged"] = cl.Hex("#808080")
    return color_map


def build_ordered_tags(unique_tags: List[str]) -> List[str]:
    """Build ordered list of tags with untagged last."""
    return [t for t in unique_tags if t != "untagged"] + ["untagged"]


def should_render_legend(unique_tags: List[str]) -> bool:
    """Return True when there is at least one tag other than untagged."""
    return any(tag != "untagged" for tag in unique_tags)


def build_legend_html(
    color_map: Dict[str, cl.Hex], note_tags: Dict[str, str], ordered_tags: List[str]
) -> str:
    tag_colors = {tag: str(color) for tag, color in color_map.items()}
    untagged_color = str(color_map["untagged"])
    rows = ""
    for tag in ordered_tags:
        color = color_map[tag]
        rows += f"""
        <tr>
            <td style="padding: 4px;">
                <div id="legend-{tag}" style="
                    width: 15px;
                    height: 15px;
                    background-color: {color};
                    border-radius: 3px;
                    cursor: pointer;
                    opacity: 1;
                    transition: opacity 0.2s;
                " onclick="toggleTag('{tag}')"></div>
            </td>
            <td style="padding: 4px; cursor: pointer;" onclick="toggleTag('{tag}')">{tag}</td>
        </tr>
        """

    legend = f"""
    <div id="legend-container" style="
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 9999;
        background: white;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 10px;
        min-width: 160px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 13px;
        user-select: none;
    ">
    <button id="toggle-legend-btn" onclick="toggleLegend()" style="
        width: 100%;
        padding: 5px 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #f5f5f5;
        cursor: pointer;
        font-size: 12px;
        transition: background 0.15s;
    "
    onmouseover="this.style.background='#e8e8e8'"
    onmouseout="this.style.background='#f5f5f5'">Filter</button>
    <div id="legend-panel" style="
        margin-top: 8px;
        display: none;
    ">
        <b style="display: block; margin-bottom: 8px; color: #333;">Tags</b>
        <span style="font-size: 11px; color: #888;">click to filter</span>
        <table style="margin-top: 6px; border-collapse: collapse;">
            {rows}
        </table>
        <div style="display: flex; gap: 6px; margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
            <button onclick="hideAllTags()" style="
                flex: 1;
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f5f5f5;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.15s;
            "
            onmouseover="this.style.background='#e8e8e8'"
            onmouseout="this.style.background='#f5f5f5'">Hide All</button>
            <button onclick="showAllTags()" style="
                flex: 1;
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f5f5f5;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.15s;
            "
            onmouseover="this.style.background='#e8e8e8'"
            onmouseout="this.style.background='#f5f5f5'">Show All</button>
        </div>
        <div style="margin-top: 6px;">
            <button id="toggle-colors-btn" onclick="toggleTagColors()" style="
                width: 100%;
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f5f5f5;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.15s;
            "
            onmouseover="this.style.background='#e8e8e8'"
            onmouseout="this.style.background='#f5f5f5'">Enable Colors</button>
        </div>
    </div>
    </div>
    <script>
        var hiddenTags = {{}};
        var nodeTags = {note_tags};
        var tagColors = {tag_colors};
        var untaggedColor = "{untagged_color}";
        var useTagColors = false;
        var legendVisible = false;

        function toggleLegend() {{
            legendVisible = !legendVisible;
            var panel = document.getElementById('legend-panel');
            panel.style.display = legendVisible ? 'block' : 'none';
        }}

        function toggleTag(tag) {{
            hiddenTags[tag] = !hiddenTags[tag];
            var el = document.getElementById('legend-' + tag);
            el.style.opacity = hiddenTags[tag] ? '0.3' : '1';

            // Hide/show the tag node itself
            var tagNodeId = 'tag_' + tag;
            var tagNode = network.body.data.nodes.get(tagNodeId);
            if (tagNode) {{
                network.body.data.nodes.update({{
                    id: tagNodeId,
                    hidden: hiddenTags[tag]
                }});
            }}

            for (var nodeId in nodeTags) {{
                if (nodeTags[nodeId] === tag) {{
                    var node = network.body.data.nodes.get(nodeId);
                    if (node) {{
                        network.body.data.nodes.update({{
                            id: nodeId,
                            hidden: hiddenTags[tag]
                        }});
                    }}
                }}
            }}
        }}

        function showAllTags() {{
            for (var tag in hiddenTags) {{
                if (hiddenTags[tag]) {{
                    hiddenTags[tag] = false;
                    var el = document.getElementById('legend-' + tag);
                    if (el) el.style.opacity = '1';

                    for (var nodeId in nodeTags) {{
                        if (nodeTags[nodeId] === tag) {{
                            var node = network.body.data.nodes.get(nodeId);
                            if (node) {{
                                network.body.data.nodes.update({{
                                    id: nodeId,
                                    hidden: false
                                }});
                            }}
                        }}
                    }}
                }}
            }}
        }}

        function hideAllTags() {{
            for (var tag in nodeTags) {{
                if (!hiddenTags[nodeTags[tag]]) {{
                    hiddenTags[nodeTags[tag]] = true;
                    var el = document.getElementById('legend-' + nodeTags[tag]);
                    if (el) el.style.opacity = '0.3';

                    for (var nodeId in nodeTags) {{
                        if (nodeTags[nodeId] === nodeTags[tag]) {{
                            var node = network.body.data.nodes.get(nodeId);
                            if (node) {{
                                network.body.data.nodes.update({{
                                    id: nodeId,
                                    hidden: true
                                }});
                            }}
                        }}
                    }}
                }}
            }}
        }}

        function applyTagColors() {{
            for (var nodeId in nodeTags) {{
                var node = network.body.data.nodes.get(nodeId);
                if (node) {{
                    var tag = nodeTags[nodeId];
                    var nodeColor = useTagColors ? (tagColors[tag] || untaggedColor) : untaggedColor;
                    network.body.data.nodes.update({{
                        id: nodeId,
                        color: nodeColor
                    }});
                }}
            }}
        }}

        function toggleTagColors() {{
            useTagColors = !useTagColors;
            var btn = document.getElementById('toggle-colors-btn');
            btn.textContent = useTagColors ? 'Disable Colors' : 'Enable Colors';
            applyTagColors();
        }}

        applyTagColors();
    </script>
    """
    return legend


def _add_ghost_node(net: Network, node_id: str) -> None:
    """Add a placeholder node for a link endpoint that has no backing note."""
    net.add_node(
        node_id,
        label=node_id.split("/")[-1],
        color={"background": "#f0f0f0", "border": "#b0b0b0"},
        size=6,
        shape="dot",
        title="unresolved link",
    )


def make_graph(
    data: Dict[str, Any],
    palette: str = "carnival",
    directed: bool = False,
    output_path: Optional[str] = None,
    orphans: str = "drop",
    show_tags: bool = True,
) -> Network:
    """Render an interactive note graph using Pyvis.

    Transforms raw zk graph data, then builds a graph with nodes colored by tag
    and sized by backlink count. Nodes and edges are keyed by the note's
    canonical ``id`` (see :func:`transform_json_data`) so links between notes in
    subdirectories resolve instead of being reported as orphans.

    Args:
        data: Raw graph data with ``notes`` and ``links`` keys.
        palette: Name of a Colorir palette to use for tag-based coloring.
        directed: Whether to render a directed network.
        output_path: If provided, saves the graph at this path; otherwise
            uses a temporary file.
        orphans: How to handle a link whose endpoint has no note. ``"drop"``
            skips the edge and warns; ``"ghost"`` renders a placeholder node
            and keeps the edge; ``"error"`` raises ``ValueError``.

    Returns:
        The built Pyvis ``Network``.
    """
    data = transform_json_data(data)

    net = Network(
        height="100vh",
        width="100%",
        directed=directed,
        cdn_resources="remote"
    )

    unique_tags: List[str] = list({note["tag"] for note in data["notes"]})
    color_map = build_color_map(unique_tags, palette)
    render_legend = should_render_legend(unique_tags)
    ordered_tags = build_ordered_tags(unique_tags)

    # Build set of node IDs for O(1) existence validation during edge processing
    node_ids = set()
    for note in data["notes"]:
        node_id = note["id"]
        node_ids.add(node_id)
        net.add_node(
            node_id,
            label=note["title"],
            color=color_map[note["tag"]],
            size=10 + 10 * np.log(note["backlinks"] + 1),
            shape="dot",
        )

    # Add tag nodes and link notes to all their tags
    if show_tags:
        for tag in unique_tags:
            if tag == "untagged":
                continue
            tag_id = f"tag_{tag}"
            net.add_node(
                tag_id,
                label=f"#{tag}",
                color=color_map[tag],
                size=10,
                shape="square",
            )
            for note in data["notes"]:
                if tag in note.get("tags", []):
                    net.add_edge(note["filenameStem"], tag_id)

    # Resolve edge endpoints. An endpoint with no note is handled per
    # ``orphans``: "ghost" renders a placeholder node and keeps the edge,
    # "error" raises, and "drop" (default) skips the edge and warns.
    ghost_ids: set = set()
    # Validate edge references and aggregate orphaned edges by missing node
    orphaned_refs: Dict[str, List[str]] = {}

    def resolve(node: str, referenced_by: str) -> bool:
        if node in node_ids or node in ghost_ids:
            return True
        if orphans == "ghost":
            _add_ghost_node(net, node)
            ghost_ids.add(node)
            return True
        if orphans == "error":
            raise ValueError(
                f"Orphaned edge endpoint '{node}' referenced by '{referenced_by}'"
            )
        orphaned_refs.setdefault(node, []).append(referenced_by)
        return False

    for link in data["links"]:
        source = link["sourcePath"]
        target = link["targetPath"]
        if not resolve(target, source):
            continue
        if not resolve(source, target):
            continue
        net.add_edge(source, target)

    # Emit aggregated warnings for each unique missing node
    for missing_node, refs in orphaned_refs.items():
        example_refs = ', '.join(refs[:3])
        if len(refs) > 3:
            example_refs += f'... and {len(refs) - 3} more'

        warnings.warn(
            f"Skipping edge(s) to missing node '{missing_node}'. "
            f"Referenced by: {example_refs}"
        )

    if output_path is None:
        with tempfile.NamedTemporaryFile(suffix=".html") as f:
            html_path = f.name
    else:
        html_path = output_path
    net.write_html(html_path)

    if render_legend:
        note_tags = {note["id"]: note["tag"] for note in data["notes"]}
        legend_html = build_legend_html(color_map, note_tags, ordered_tags)
        with open(html_path, "r+") as f:
            html = f.read()
            html = html.replace("</body>", legend_html + "\n</body>")
            f.seek(0)
            f.write(html)
            f.truncate()

    webbrowser.open(f"file://{html_path}")

    return net
