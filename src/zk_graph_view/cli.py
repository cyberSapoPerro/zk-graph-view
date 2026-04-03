import argparse
import networkx as nx
from halo import Halo

from zk_graph_view.api import (
    ensure_zk_dir_exist,
    get_json_from_cli,
    get_json_from_input_path,
    transform_json_data,
)
from zk_graph_view.graph import make_interactive_graph, make_static_graph


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
        "-c",
        "--colors",
        metavar="PALETTE",
        default="carnival",
        help="Color palette name (see colorir docs: https://colorir.readthedocs.io/en/latest/builtin_palettes.html)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Path to output file (HTML for interactive, image for static)",
    )

    parser.add_argument(
        "--static",
        action="store_true",
        help="Render a static graph instead of interactive",
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    colors = args.colors

    if input_path:
        data = get_json_from_input_path(input_path)
    else:
        data = get_json_from_cli()

    if not args.static:
        with Halo(text="Generating interactive graph", spinner="dots"):
            make_interactive_graph(data, palette=colors, output_path=output_path)
    else:
        data = transform_json_data(data)

        G = nx.DiGraph()
        for note in data["notes"]:
            G.add_node(note["filenameStem"])
        for link in data["links"]:
            G.add_edge(link["sourcePath"], link["targetPath"])

        if len(G) < 1500:
            try:
                layout = nx.kamada_kawai_layout(G)
            except Exception:
                layout = nx.spring_layout(G, seed=42)
        else:
            layout = nx.spring_layout(G, seed=42)

        with Halo(text="Generating static graph", spinner="dots"):
            make_static_graph(
                data, palette=colors, layout=layout, output_path=output_path
            )


if __name__ == "__main__":
    main()
