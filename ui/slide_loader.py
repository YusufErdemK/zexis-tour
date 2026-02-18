"""
slide_loader.py
~~~~~~~~~~~~~~~
Loads and validates the slide definitions from slides.json.
Returns a list of SlideData dataclass instances.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SlideData:
    """Represents a single onboarding slide."""
    id: str
    title: str
    description: str
    icon: Optional[str] = None          # Freedesktop icon name
    image_path: Optional[str] = None    # Absolute path to an image asset
    accent: str = "blue"                # Accent colour hint (unused by GTK directly)
    is_final: bool = False              # True for the last/completion slide


def load_slides(json_path: str, assets_dir: str) -> List[SlideData]:
    """
    Parse slides.json and return a validated list of SlideData objects.

    Parameters
    ----------
    json_path   : Absolute path to slides.json
    assets_dir  : Absolute path to the assets/ directory, used to resolve
                  relative image_path values declared in the JSON.

    Raises
    ------
    FileNotFoundError  – if slides.json does not exist.
    ValueError         – if a slide is missing required fields.
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"slides.json not found at: {json_path}")

    with open(json_path, "r", encoding="utf-8") as fh:
        raw: list = json.load(fh)

    slides: List[SlideData] = []
    for idx, entry in enumerate(raw):
        # --- required fields ---
        for key in ("id", "title", "description"):
            if key not in entry:
                raise ValueError(
                    f"Slide #{idx} is missing required field '{key}'."
                )

        # --- resolve image path relative to assets/ ---
        image_path: Optional[str] = None
        if "image_path" in entry and entry["image_path"]:
            candidate = os.path.join(assets_dir, entry["image_path"])
            if os.path.isfile(candidate):
                image_path = candidate
            # If the file doesn't exist we silently skip it; the icon
            # will be used as a fallback in the UI.

        slides.append(SlideData(
            id=entry["id"],
            title=entry["title"],
            description=entry["description"],
            icon=entry.get("icon"),
            image_path=image_path,
            accent=entry.get("accent", "blue"),
            is_final=bool(entry.get("is_final", False)),
        ))

    if not slides:
        raise ValueError("slides.json must contain at least one slide.")

    return slides
