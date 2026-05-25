import tempfile
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


def make_graph(
    data: Dict[str, Any],
    palette: str,
    directed: bool,
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

    if render_legend:
        note_tags = {note["filenameStem"]: note["tag"] for note in data["notes"]}
        legend_html = build_legend_html(color_map, note_tags, ordered_tags)
        with open(html_path, "r+") as f:
            html = f.read()
            html = html.replace("</body>", legend_html + "\n</body>")
            f.seek(0)
            f.write(html)
            f.truncate()

    webbrowser.open(f"file://{html_path}")
