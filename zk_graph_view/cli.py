import argparse
import json
import subprocess
import tempfile
import webbrowser

import colorir as cl
import numpy as np
from pyvis.network import Network


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
        net.write_html(html_path)
        webbrowser.open(f"file://{html_path}")
    else:
        net.write_html(output_path)
        webbrowser.open(f"file://{output_path}")


def main():
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
