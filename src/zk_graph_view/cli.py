import argparse

from zk_graph_view.api import (
    ensure_zk_dir_exist,
    get_json_from_cli,
    get_json_from_input_path,
)
from zk_graph_view.graph import make_graph


def main():
    ensure_zk_dir_exist()

    parser = argparse.ArgumentParser(
        description="Visualize your zk graph. Run inside a zk directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="FILE",
        help="Path to input JSON file (if omitted, uses `zk graph --format=json`)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Path to output file (HTML for interactive, image for static)",
    )

    parser.add_argument(
        "-c",
        "--colors",
        metavar="PALETTE",
        default="carnival",
        help="Color palette name (see colorir docs: https://colorir.readthedocs.io/en/latest/builtin_palettes.html)",
    )

    parser.add_argument(
        "--directed",
        metavar="BOOL",
        default=False,
        help="Render a directed network graph"
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    colors = args.colors
    directed = args.directed

    if input_path:
        data = get_json_from_input_path(input_path)
    else:
        data = get_json_from_cli()

    make_graph(
        data,
        palette=colors,
        directed=directed,
        output_path=output_path
    )


if __name__ == "__main__":
    main()
