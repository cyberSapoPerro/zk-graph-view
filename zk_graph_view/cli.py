import json
import subprocess
import webbrowser
import tempfile
from pyvis.network import Network
import colorir as cl


def get_zk_graph():
    result = subprocess.run(
        ["zk", "graph", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return data


def make_html_graph():
    data = get_zk_graph()
    net = Network(height="100vh", width="100%", directed=True)

    # --- Tags ---
    tags = [note["tags"][0] if note["tags"] else "untagged" for note in data["notes"]]

    # -- Color map ---
    grad = cl.PolarGrad(["ffff00", "ff00ff"])  # Creates a gradient from yellow to magenta
    palette = cl.StackPalette(grad.n_colors(len(tags)))
    palette *= cl.HCLab(1, 0.5, 1)  # Desaturates the palette 50% to get a more pleasing look
    color_map = {tag: color for tag, color in zip(tags, palette)}
    color_map["untagged"] = cl.Hex("#808080")

    # --- Nodes ---
    for note in data["notes"]:
        node_id = note["filenameStem"]  # unique ID
        label = note["title"]
        if note["tags"]:
            tag = note["tags"][0]
        else:
            tag = "untagged"
        net.add_node(node_id, label=label, color=color_map[tag])

    # --- Edges ---
    for link in data["links"]:
        source = link["sourcePath"].replace(".md", "")
        target = link["targetPath"].replace(".md", "")
        net.add_edge(source, target)

    # --- Open the graph ---
    with tempfile.NamedTemporaryFile(suffix=".html") as f:
        html_path = f.name
    net.write_html(html_path)
    return html_path


def main():
    html_path = make_html_graph()
    webbrowser.open(f"file://{html_path}")

if __name__ == "__main__":
    main()
