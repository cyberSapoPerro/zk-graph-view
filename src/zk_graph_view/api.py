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

def get_json_from_pipe() -> Dict[str, Any]:
    raw = sys.stdin.read()
    data = json.loads(raw)
    return data


def _strip_md(path: str) -> str:
    """Return a notebook-relative path without its trailing .md extension."""
    return path[:-3] if path.endswith(".md") else path


def transform_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw zk graph JSON into a structured format.

    Assigns each note a canonical ``id`` (its notebook-relative ``path`` with the
    .md suffix removed), which is the same identifier space the links use via
    ``sourcePath`` / ``targetPath``. Keying nodes and edges by this shared id is
    what lets notes in subdirectories resolve their links; the bare
    ``filenameStem`` does not match the directory-qualified link endpoints.

    Also computes a backlink count per note and adds a singular ``tag`` key
    derived from the note's ``tags`` list.

    Args:
        json_data: Raw graph data with ``notes`` and ``links`` keys.

    Returns:
        Dict with ``notes`` (each containing ``id``, ``tag``, ``backlinks``, and
        original keys) and ``links`` (with ``sourcePath`` and ``targetPath``
        cleaned of the .md suffix).
    """
    links = [
        {
            "sourcePath": _strip_md(link["sourcePath"]),
            "targetPath": _strip_md(link["targetPath"]),
        }
        for link in json_data["links"]
    ]

    backlinks: Dict[str, int] = {
        _strip_md(note.get("path") or note["filenameStem"]): 0
        for note in json_data["notes"]
    }
    for link in links:
        target = link["targetPath"]
        if target in backlinks:
            backlinks[target] += 1

    notes = []
    for note in json_data["notes"]:
        note_id = _strip_md(note.get("path") or note["filenameStem"])
        tags = note.get("tags") or []
        notes.append(
            {
                **note,
                "id": note_id,
                "tag": tags[0] if tags else "untagged",
                "backlinks": backlinks[note_id],
            }
        )

    return {"notes": notes, "links": links}
