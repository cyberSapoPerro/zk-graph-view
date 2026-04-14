# Copilot instructions for `zk-graph-view`

## Build, test, and lint commands

This repository currently does **not** define dedicated build, lint, or test commands in `pyproject.toml` (no pytest/ruff/mypy/tox/nox config is present).

Useful project commands that do exist:

```bash
# Install locally in editable mode
pipx install -e .

# Or install as a uv tool (recommended in README)
uv tool install zk-graph-view

# Run the CLI inside a zk notebook directory
zk-graph-view

# Generate static output
zk-graph-view --static -o graph.png
```

Single-test command: **not available** (no test suite is currently included in this repository).

## High-level architecture

The runtime flow spans `cli.py`, `api.py`, and `graph.py`:

1. `cli.main()` (`src/zk_graph_view/cli.py`) is the entrypoint (`project.scripts`), parses args, and always calls `ensure_zk_dir_exist()` first.
2. Input data is loaded either from:
   - `zk graph --format=json` via `get_json_from_cli()`, or
   - `--input` JSON via `get_json_from_input_path()`.
3. Interactive mode calls `make_interactive_graph(...)`:
   - transforms raw JSON,
   - builds a directed Pyvis graph,
   - colors nodes by tag, sizes nodes by backlink count,
   - writes HTML and injects a custom in-page legend/filter script,
   - opens the result in a browser.
4. Static mode computes a NetworkX layout in `cli.py` (Kamada-Kawai under 1500 nodes; spring layout otherwise/fallback) and calls `make_static_graph(...)` to render PNG with Matplotlib.

## Key conventions in this codebase

- **Execution context is strict:** `.zk/` must exist in the current directory because `ensure_zk_dir_exist()` runs before any mode selection (even when `--input` is provided).
- **Canonical transformed graph shape:** graph renderers rely on `transform_json_data()` producing:
  - `notes[*].tag` as the **first** tag (or `"untagged"`),
  - `notes[*].backlinks` computed from inbound links,
  - link paths normalized by removing `.md`.
- **Visual encoding is stable:**
  - node size formula is `10 + 10 * log(backlinks + 1)`,
  - `"untagged"` is always gray (`#808080`),
  - interactive legend is shown only when at least one non-`untagged` tag exists.
- **Output behavior differs by mode:**
  - interactive mode can use a temporary HTML file when `--output` is omitted and always attempts to open a browser,
  - static mode requires an explicit output path and raises `ValueError` if missing.
