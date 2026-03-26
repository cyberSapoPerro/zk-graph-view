import os
import sys
import argparse
import json
import subprocess
import tempfile
import webbrowser

import colorir as cl
import numpy as np
from pyvis.network import Network


def ensure_zk_dir_exist():
    if not os.path.isdir(".zk"):
        print("Error: .zk directory not found in the current directory.", file=sys.stderr)
        sys.exit(1)


def get_json_from_cli():
    result = subprocess.run(
        ["zk", "graph", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return data


def get_json_from_input_path(input_path):
    with open(input_path) as f:
        data = json.load(f)
    return data


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


def make_graph(
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

    # -- Make the lengend ---
    legend_html = build_legend_html(color_map)
    with open(html_path, "r+") as f:
        html = f.read()
        html = html.replace("</body>", legend_html + "\n</body>")
        f.seek(0)
        f.write(html)
        f.truncate()

    webbrowser.open(f"file://{html_path}")


def main():
    ensure_zk_dir_exist()

    parser = argparse.ArgumentParser(
        description="Visualize your zk graph. Run inside a zk directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i", "--input",
        metavar="FILE",
        help="Path to input JSON file (if omitted, uses `zk graph --format=json`)"
    )

    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Path to output HTML file (if omitted, don't stores the graph)"
    )

    parser.add_argument(
        "-c", "--colors",
        metavar="PALETTE",
        default="carnival",
        help="Color palette name (see colorir docs: https://colorir.readthedocs.io/en/latest/builtin_palettes.html)"
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    colors = args.colors

    if input_path:
        data = get_json_from_input_path(input_path)
    else:
        data = get_json_from_cli()

    make_graph(data, palette=colors, output_path=output_path)


if __name__ == "__main__":
    main()
