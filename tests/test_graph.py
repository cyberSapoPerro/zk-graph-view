"""Tests for zk_graph_view.graph module."""

import warnings
import pytest
from zk_graph_view.api import transform_json_data
from zk_graph_view.graph import make_graph


@pytest.fixture
def sample_data():
    """Sample graph data for testing."""
    return {
        "notes": [
            {
                "filename": "note1.md",
                "filenameStem": "note1",
                "path": "note1.md",
                "title": "Note 1",
                "tag": "untagged",
                "backlinks": 0
            },
            {
                "filename": "note2.md",
                "filenameStem": "note2",
                "path": "note2.md",
                "title": "Note 2",
                "tag": "untagged",
                "backlinks": 1
            }
        ],
        "links": [
            {
                "sourcePath": "note1",
                "targetPath": "note2"
            }
        ]
    }


def test_orphaned_target_node():
    """Test that edges to missing target nodes are skipped and warnings are emitted."""
    data = {
        "notes": [
            {
                "filename": "note1.md",
                "filenameStem": "note1",
                "path": "note1.md",
                "title": "Note 1",
                "tag": "untagged",
                "backlinks": 0
            }
        ],
        "links": [
            {
                "sourcePath": "note1",
                "targetPath": "missing-note"
            }
        ]
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Suppress browser opening for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            make_graph(data)

        assert len(w) == 1
        assert "missing-note" in str(w[0].message)
        assert "note1" in str(w[0].message)


def test_orphaned_source_node():
    """Test that edges from missing source nodes are skipped and warnings are emitted."""
    data = {
        "notes": [
            {
                "filename": "note2.md",
                "filenameStem": "note2",
                "path": "note2.md",
                "title": "Note 2",
                "tag": "untagged",
                "backlinks": 0
            }
        ],
        "links": [
            {
                "sourcePath": "missing-note",
                "targetPath": "note2"
            }
        ]
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Suppress browser opening for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            make_graph(data)

        assert len(w) == 1
        assert "missing-note" in str(w[0].message)


def test_valid_edges_work():
    """Test that valid edges still function correctly without warnings."""
    data = {
        "notes": [
            {
                "filename": "note1.md",
                "filenameStem": "note1",
                "path": "note1.md",
                "title": "Note 1",
                "tag": "untagged",
                "backlinks": 0
            },
            {
                "filename": "note2.md",
                "filenameStem": "note2",
                "path": "note2.md",
                "title": "Note 2",
                "tag": "untagged",
                "backlinks": 1
            }
        ],
        "links": [
            {
                "sourcePath": "note1",
                "targetPath": "note2"
            }
        ]
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Suppress browser opening for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            make_graph(data)

        # Should not warn for valid edges
        assert len(w) == 0


def test_aggregated_warnings():
    """Test that multiple orphaned edges to same missing node produce only one warning."""
    data = {
        "notes": [
            {
                "filename": "note1.md",
                "filenameStem": "note1",
                "path": "note1.md",
                "title": "Note 1",
                "tag": "untagged",
                "backlinks": 0
            },
            {
                "filename": "note2.md",
                "filenameStem": "note2",
                "path": "note2.md",
                "title": "Note 2",
                "tag": "untagged",
                "backlinks": 0
            },
            {
                "filename": "note3.md",
                "filenameStem": "note3",
                "path": "note3.md",
                "title": "Note 3",
                "tag": "untagged",
                "backlinks": 0
            }
        ],
        "links": [
            {
                "sourcePath": "note1",
                "targetPath": "missing"
            },
            {
                "sourcePath": "note2",
                "targetPath": "missing"
            },
            {
                "sourcePath": "note3",
                "targetPath": "missing"
            }
        ]
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Suppress browser opening for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            make_graph(data)

        # Should only warn once per missing node
        assert len(w) == 1
        assert "missing" in str(w[0].message)


def test_multiple_missing_nodes():
    """Test that each missing node gets its own warning message."""
    data = {
        "notes": [
            {
                "filename": "note1.md",
                "filenameStem": "note1",
                "path": "note1.md",
                "title": "Note 1",
                "tag": "untagged",
                "backlinks": 0
            },
            {
                "filename": "note2.md",
                "filenameStem": "note2",
                "path": "note2.md",
                "title": "Note 2",
                "tag": "untagged",
                "backlinks": 0
            }
        ],
        "links": [
            {
                "sourcePath": "note1",
                "targetPath": "missing-node-1"
            },
            {
                "sourcePath": "note2",
                "targetPath": "missing-node-2"
            }
        ]
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Suppress browser opening for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            make_graph(data)

        # Should warn once per missing node
        assert len(w) == 2
        missing_nodes = [str(warning.message) for warning in w]
        assert any("missing-node-1" in msg for msg in missing_nodes)
        assert any("missing-node-2" in msg for msg in missing_nodes)


def test_backlinks_counted_for_subdir_paths():
    """Backlinks match notes to link targets by full path, not bare stem."""
    data = {
        "notes": [
            {"filenameStem": "a", "path": "pages/a.md", "title": "A", "tags": []},
            {"filenameStem": "b", "path": "pages/b.md", "title": "B", "tags": []},
            {"filenameStem": "hub", "path": "pages/hub.md", "title": "Hub", "tags": []},
        ],
        "links": [
            {"sourcePath": "pages/a.md", "targetPath": "pages/hub.md"},
            {"sourcePath": "pages/b.md", "targetPath": "pages/hub.md"},
        ],
    }

    out = transform_json_data(data)
    by_id = {note["id"]: note for note in out["notes"]}

    assert by_id["pages/hub"]["backlinks"] == 2
    assert by_id["pages/a"]["backlinks"] == 0


def test_subdir_link_connects_real_nodes():
    """A link between two notes in subdirectories is a real edge, not an orphan."""
    data = {
        "notes": [
            {"filenameStem": "n1", "path": "pages/n1.md", "title": "N1", "tags": []},
            {"filenameStem": "n2", "path": "journals/n2.md", "title": "N2", "tags": []},
        ],
        "links": [
            {"sourcePath": "pages/n1.md", "targetPath": "journals/n2.md"},
        ],
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with pytest.MonkeyPatch().context() as m:
            m.setattr("zk_graph_view.graph.webbrowser.open", lambda x: None)
            net = make_graph(data)

    assert [str(warning.message) for warning in w] == []
    assert set(net.get_nodes()) == {"pages/n1", "journals/n2"}
    assert any(
        edge["from"] == "pages/n1" and edge["to"] == "journals/n2"
        for edge in net.edges
    )
