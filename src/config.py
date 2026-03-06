"""Global configuration and path management."""

import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = Path(os.environ.get("CACHE_DIR", PROJECT_ROOT / "cache"))
THEMES_DIR = PROJECT_ROOT / "themes"
FONTS_DIR = PROJECT_ROOT / "fonts"
POSTERS_DIR = PROJECT_ROOT / "posters"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
POSTERS_DIR.mkdir(exist_ok=True)

# Constants
FILE_ENCODING = "utf-8"
MAX_POSTER_DIMENSION = 20  # inches
DEFAULT_DISTANCE = 18000  # meters
DEFAULT_THEME = "terracotta"
DEFAULT_WIDTH = 12  # inches
DEFAULT_HEIGHT = 16  # inches
