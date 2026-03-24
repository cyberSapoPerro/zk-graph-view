import argparse

import json
from pyvis.network import Network

def make_html_graph(json_path, html_path):
    with open(json_path) as f:
        data = json.load(f)

    net = Network(height="100vh", width="100%", directed=True)

    # --- Nodes ---
    for note in data["notes"]:
        node_id = note["filenameStem"]  # unique ID
        label = note["title"]
        net.add_node(node_id, label=label)

    # --- Edges ---
    for link in data["links"]:
        source = link["sourcePath"].replace(".md", "")
        target = link["targetPath"].replace(".md", "")
        net.add_edge(source, target)

    net.write_html(html_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")

    args = parser.parse_args()

    make_html_graph(args.input, args.output)


if __name__ == "__main__":
    main()
