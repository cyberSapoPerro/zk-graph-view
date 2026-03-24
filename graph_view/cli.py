import json
import subprocess
import webbrowser
import tempfile
from pyvis.network import Network


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
    with tempfile.NamedTemporaryFile(suffix=".html") as f:
        html_path = f.name
    net.write_html(html_path)
    return html_path


def main():
    html_path = make_html_graph()
    webbrowser.open(f"file://{html_path}")

if __name__ == "__main__":
    main()
