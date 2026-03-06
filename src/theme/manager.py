"""Theme loading and management."""

import json
import os
from typing import Dict

from src.config import FILE_ENCODING, THEMES_DIR


def get_available_themes() -> list[str]:
    """Get list of available theme names."""
    if not THEMES_DIR.exists():
        THEMES_DIR.mkdir(parents=True, exist_ok=True)
        return []

    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith(".json"):
            themes.append(file[:-5])  # Remove .json
    return themes


def load_theme(theme_name: str = "terracotta") -> Dict[str, str]:
    """
    Load theme from JSON file.

    Args:
        theme_name: Name of theme (without .json)

    Returns:
        Theme dictionary with color mappings
    """
    theme_file = THEMES_DIR / f"{theme_name}.json"

    if not theme_file.exists():
        print(f"⚠ Theme '{theme_name}' not found. Using terracotta.")
        return _get_default_theme()

    try:
        with open(theme_file, "r", encoding=FILE_ENCODING) as f:
            theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if "description" in theme:
            print(f"  {theme['description']}")
        return theme
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠ Error loading theme: {e}. Using terracotta.")
        return _get_default_theme()


def _get_default_theme() -> Dict[str, str]:
    """Get fallback terracotta theme."""
    return {
        "name": "Terracotta",
        "description": "Mediterranean warmth - burnt orange and clay tones",
        "bg": "#F5EDE4",
        "text": "#8B4513",
        "gradient_color": "#F5EDE4",
        "water": "#A8C4C4",
        "parks": "#E8E0D0",
        "road_motorway": "#A0522D",
        "road_primary": "#B8653A",
        "road_secondary": "#C9846A",
        "road_tertiary": "#D9A08A",
        "road_residential": "#E5C4B0",
        "road_default": "#D9A08A",
        "rails": "#949494",
    }


def print_theme_list() -> None:
    """Print all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found.")
        return

    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = THEMES_DIR / f"{theme_name}.json"
        try:
            with open(theme_path, "r", encoding=FILE_ENCODING) as f:
                theme_data = json.load(f)
                display_name = theme_data.get("name", theme_name)
                description = theme_data.get("description", "")
        except (OSError, json.JSONDecodeError):
            display_name = theme_name
            description = ""
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()
