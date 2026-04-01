import os
import sys
import subprocess
import json
from typing import Any, Dict


def ensure_zk_dir_exist() -> None:
    """Ensure a .zk directory exists in the current directory.

    Exits with an error message if not found.
    """
    if not os.path.isdir(".zk"):
        print(
            "Error: .zk directory not found in the current directory", file=sys.stderr
        )
        sys.exit(1)


def get_json_from_cli() -> Dict[str, Any]:
    """Get zk graph data by calling the zk CLI.

    Runs ``zk graph --format=json`` and parses the output.

    Returns:
        Parsed JSON data from the zk graph command.
    """
    result = subprocess.run(
        ["zk", "graph", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return data


def get_json_from_input_path(input_path: str) -> Dict[str, Any]:
    """Load zk graph data from a JSON file.

    Args:
        input_path: Path to the JSON file.

    Returns:
        Parsed JSON data from the file.
    """
    with open(input_path) as f:
        data = json.load(f)
    return data


def transform_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw zk graph JSON into a structured format.

    Normalizes note paths by removing .md suffixes, computes backlink counts,
    and adds a singular ``tag`` key to each note derived from its ``tags`` list.

    Args:
        json_data: Raw graph data with ``notes`` and ``links`` keys.

    Returns:
        Dict with ``notes`` (each containing ``filenameStem``, ``title``, ``tag``,
        ``backlinks``, and original keys) and ``links`` (with ``sourcePath`` and
        ``targetPath`` cleaned of .md suffix).
    """
    backlinks: Dict[str, int] = {}
    for note in json_data["notes"]:
        note_id = note["filenameStem"]
        backlinks[note_id] = sum(
            1
            for link in json_data["links"]
            if note_id == link["targetPath"].replace(".md", "")
        )

    notes = [
        {
            **note,
            "tag": note["tags"][0] if note["tags"] else "untagged",
            "backlinks": backlinks[note["filenameStem"]],
        }
        for note in json_data["notes"]
    ]

    links = [
        {
            "sourcePath": link["sourcePath"].replace(".md", ""),
            "targetPath": link["targetPath"].replace(".md", ""),
        }
        for link in json_data["links"]
    ]

    return {"notes": notes, "links": links}
