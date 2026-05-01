# zk-graph-view

Visualize your Zettelkasten graph from [`zk`](https://github.com/zk-org/zk) as an interactive HTML network.

![Watch the demo](assets/demo.gif)

---

## Features

- Set node size based on the number of connections
- Visualize networks interactively
- Apply tag-based coloring and filtering
- Render directed or undirected graphs
- Choose the color palette (*optional*)
- Save the HTML output (*optional*)

---

## Installation

Using `pipx`

```bash
pipx install zk-graph-view
```

or using `uv`:

```bash
uv tool install zk-graph-view
```

> Using `uv` is recommended.

### Manual

```bash
git clone https://github.com/cyberSapoPerro/zk-graph-view.git
cd zk-graph-view
pipx install -e .
````

## Usage

Run the tool inside a valid `zk` notebook directory:

```bash
zk-graph-view
```

This will generate an interactive HTML visualization.
