from typing import Dict, List

import colorir as cl


def build_color_map(unique_tags: List[str], palette: str) -> Dict[str, cl.Hex]:
    """Build a color map from a list of tags and a palette name."""
    palette_obj = cl.StackPalette.load(
        palette, palettes_dir=cl.config.USR_PALETTES_DIR
    ).resize(len(unique_tags))
    color_map = {tag: color for tag, color in zip(unique_tags, palette_obj)}
    color_map["untagged"] = cl.Hex("#808080")
    return color_map
