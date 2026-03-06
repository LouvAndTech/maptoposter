"""Font loading from local and Google Fonts."""

import re
from pathlib import Path
from typing import Optional

import requests

from src.config import FILE_ENCODING, FONTS_DIR
from src.callbacks import emit_status

FONTS_CACHE_DIR = FONTS_DIR / "cache"


def download_google_font(
    font_family: str, weights: Optional[list] = None
) -> Optional[dict]:
    """
    Download font family from Google Fonts.

    Args:
        font_family: Google Fonts family name (e.g., 'Noto Sans JP')
        weights: Font weights to download [300, 400, 700]

    Returns:
        Dict with 'light', 'regular', 'bold' keys mapping to paths
    """
    if weights is None:
        weights = [300, 400, 700]

    FONTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    font_name_safe = font_family.replace(" ", "_").lower()
    font_files = {}

    try:
        weights_str = ";".join(map(str, weights))
        api_url = "https://fonts.googleapis.com/css2"
        params = {"family": f"{font_family}:wght@{weights_str}"}
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        css_content = response.text

        weight_url_map = {}
        font_face_blocks = re.split(r"@font-face\s*\{", css_content)

        for block in font_face_blocks[1:]:
            weight_match = re.search(r"font-weight:\s*(\d+)", block)
            if not weight_match:
                continue

            weight = int(weight_match.group(1))
            url_match = re.search(r"url\((https://[^)]+\.(woff2|ttf))\)", block)
            if url_match:
                weight_url_map[weight] = url_match.group(1)

        weight_map = {300: "light", 400: "regular", 700: "bold"}

        for weight in weights:
            weight_key = weight_map.get(weight, "regular")
            weight_url = weight_url_map.get(weight)

            if not weight_url and weight_url_map:
                closest_weight = min(
                    weight_url_map.keys(), key=lambda x: abs(x - weight)
                )
                weight_url = weight_url_map[closest_weight]

            if weight_url:
                file_ext = "woff2" if weight_url.endswith(".woff2") else "ttf"
                font_filename = f"{font_name_safe}_{weight_key}.{file_ext}"
                font_path = FONTS_CACHE_DIR / font_filename

                if not font_path.exists():
                    emit_status(f"Downloading {font_family} {weight_key}...")
                    print(f"  Downloading {font_family} {weight_key}...")
                    try:
                        font_response = requests.get(weight_url, timeout=10)
                        font_response.raise_for_status()
                        font_path.write_bytes(font_response.content)
                    except Exception as e:
                        emit_status(f"Failed to download {font_family} {weight_key}: {e}")
                        print(f"  ⚠ Failed to download {weight_key}: {e}")
                        continue
                else:
                    emit_status(f"Using cached {font_family} {weight_key}")
                    print(f"  Using cached {font_family} {weight_key}")

                font_files[weight_key] = str(font_path)

        if "regular" not in font_files and font_files:
            font_files["regular"] = list(font_files.values())[0]
        if "bold" not in font_files and "regular" in font_files:
            font_files["bold"] = font_files["regular"]
        if "light" not in font_files and "regular" in font_files:
            font_files["light"] = font_files["regular"]

        return font_files if font_files else None

    except Exception as e:
        print(f"⚠ Error downloading Google Font '{font_family}': {e}")
        return None


def load_fonts(font_family: Optional[str] = None) -> Optional[dict]:
    """
    Load fonts (local or Google Fonts).

    Args:
        font_family: Google Fonts family name, or None for local Roboto

    Returns:
        Dict with 'light', 'regular', 'bold' keys, or None if fails
    """
    if font_family and font_family.lower() != "roboto":
        emit_status(f"Loading Google Font: {font_family}")
        print(f"Loading Google Font: {font_family}")
        fonts = download_google_font(font_family)
        if fonts:
            emit_status(f"Font '{font_family}' loaded successfully")
            print(f"✓ Font '{font_family}' loaded successfully")
            return fonts
        emit_status(f"Failed to load '{font_family}', falling back to Roboto")
        print(f"⚠ Failed to load '{font_family}', falling back to Roboto")

    fonts = {
        "bold": str(FONTS_DIR / "Roboto-Bold.ttf"),
        "regular": str(FONTS_DIR / "Roboto-Regular.ttf"),
        "light": str(FONTS_DIR / "Roboto-Light.ttf"),
    }

    for _weight, path in fonts.items():
        if not Path(path).exists():
            print(f"⚠ Font not found: {path}")
            return None

    return fonts
