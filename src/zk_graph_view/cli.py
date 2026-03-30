import os
import sys
import argparse
import json
import subprocess

from zk_graph_view.graph import (
    make_interactive_graph, 
    make_static_graph,
)


def ensure_zk_dir_exist():
    if not os.path.isdir(".zk"):
        print("Error: .zk directory not found in the current directory", file=sys.stderr)
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

    parser.add_argument(
        "--static",
        action="store_true",
        help="Make a static graph (recomended for large notebooks of ~1k notes)"
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    colors = args.colors

    if input_path:
        data = get_json_from_input_path(input_path)
    else:
        data = get_json_from_cli()

    print(f"static: {args.static}")

    if not args.static:
        make_interactive_graph(data, palette=colors, output_path=output_path)
    else:
        make_static_graph(data, colors, output_path)


if __name__ == "__main__":
    main()
