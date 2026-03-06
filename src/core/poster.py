"""Main poster generation logic."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import osmnx as ox
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from tqdm import tqdm

from src.config import POSTERS_DIR
from src.data import fetch_features, fetch_graph
from src.theme import load_theme
from src.utils import Z_ORDERS, space_city_name
from .renderer import create_gradient_fade, get_crop_limits, get_edge_colors_and_widths, parks_renderer, water_renderer, railways_renderer
from src.callbacks import emit_progress, emit_status



def generate_output_filename(city: str, theme_name: str, output_format: str) -> str:
    """Generate unique output filename."""
    POSTERS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(" ", "_")
    filename = f"{city_slug}_{theme_name}_{timestamp}.{output_format.lower()}"
    return str(POSTERS_DIR / filename)


def create_poster(
    city: str,
    country: str,
    point: tuple[float, float],
    dist: int,
    output_file: str,
    output_format: str = "png",
    width: float = 12,
    height: float = 16,
    metric: bool = False,
    country_label: Optional[str] = None,
    display_city: Optional[str] = None,
    display_country: Optional[str] = None,
    fonts: Optional[dict] = None,
    exclude_railways: bool = False,
    theme_dict: Optional[dict] = None,
    include_oceans: bool = False,
):
    """
    Generate a complete map poster.

    Args:
        city: City name
        country: Country name
        point: (latitude, longitude) center
        dist: Map radius in meters
        output_file: Output file path
        output_format: "png", "svg", or "pdf"
        width: Poster width in inches (if metric=True, treated as cm)
        height: Poster height in inches (if metric=True, treated as cm)
        metric: Whether to use metric units
        country_label: Override country text
        display_city: Custom city name for display
        display_country: Custom country name for display
        fonts: Font dict from font_management.load_fonts()
        exclude_railways: Skip railways layer
        theme_dict: Theme dictionary (if not provided, loaded)
        include_oceans: Whether to include ocean features

    Raises:
        RuntimeError: If OSM data fetch fails
    """
    display_city = display_city or city
    display_country = display_country or country_label or country

    print(f"\nGenerating map for {display_city}, {display_country}...")
    emit_status("If the data is not cached this may take a few moments.")

    # Load theme if not provided
    if theme_dict is None:
        theme_dict = load_theme()

    compensated_dist = dist * (max(height, width) / min(height, width)) / 4

    # Fetch data with progress bar
    total_downloads = 3 if exclude_railways else 4
    with tqdm(
        total=total_downloads,
        desc="Fetching map data",
        unit="step",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
    ) as pbar:
        
        pbar.set_description("Downloading street network")
        emit_status("Downloading street network")
        emit_progress("Downloading street network", 0, total_downloads)
        g = fetch_graph(point, compensated_dist)
        if g is None:
            raise RuntimeError("Failed to retrieve street network data.")
        pbar.update(1)
        emit_progress("Downloaded street network", 1, total_downloads)

        pbar.set_description("Downloading water features")
        emit_status("Downloading water features")
        emit_progress("Downloading water features", 1, total_downloads)
        water = fetch_features(
            point,
            compensated_dist,
            tags={
                "natural": ["water", "bay", "strait", "coastline", "sea", "ocean"],
                "waterway": ["riverbank", "river", "canal", "dock", "basin"],
                "place": ["sea", "ocean", "bay"],
                "water": True
            },
            name="water",
        )
        pbar.update(1)
        emit_progress("Downloaded water features", 2, total_downloads)

        pbar.set_description("Downloading parks/green spaces")
        emit_status("Downloading parks/green spaces")
        emit_progress("Downloading parks/green spaces", 2, total_downloads)
        parks = fetch_features(
            point,
            compensated_dist,
            tags={"leisure": "park", "landuse": "grass"},
            name="parks",
        )
        pbar.update(1)
        emit_progress("Downloaded parks/green spaces", 3, total_downloads)

        railways = None
        if not exclude_railways:
            pbar.set_description("Downloading railways")
            emit_status("Downloading railways")
            emit_progress("Downloading railways", 3, total_downloads)
            try:
                railways = fetch_features(
                    point,
                    compensated_dist,
                    tags={"railway": "rail"},
                    name="railways",
                )
            except Exception as e:
                print(f"Error fetching railways: {e}")
            pbar.update(1)
            emit_progress("Downloaded railways", 4, total_downloads)

    print("✓ All data retrieved successfully!")

    # Render
    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(width, height), facecolor=theme_dict["bg"])
    ax.set_facecolor(theme_dict["bg"])
    ax.set_position((0.0, 0.0, 1.0, 1.0))

    g_proj = ox.project_graph(g)

    # Plot water
    if water is not None and not water.empty:
        crop_xlim, crop_ylim = get_crop_limits(g_proj, point, fig, compensated_dist)
        water_renderer(ax, water, g_proj, theme_dict, crop_xlim, crop_ylim, include_oceans, parks)

    # Plot parks
    if parks is not None and not parks.empty:
        parks_renderer(ax, parks, g_proj, theme_dict)

    # Plot railways
    if railways is not None and not railways.empty:
        railways_renderer(ax, railways, g_proj, theme_dict, compensated_dist)

    # Plot roads
    print("Applying road hierarchy colors...")
    edge_colors, edge_widths = get_edge_colors_and_widths(g_proj, theme_dict)

    crop_xlim, crop_ylim = get_crop_limits(g_proj, point, fig, compensated_dist)
    ox.plot_graph(
        g_proj,
        ax=ax,
        bgcolor=theme_dict["bg"],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False,
        close=False,
    )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(crop_xlim)
    ax.set_ylim(crop_ylim)

    # Gradients
    create_gradient_fade(ax, theme_dict["gradient_color"], location="bottom", zorder=10)
    create_gradient_fade(ax, theme_dict["gradient_color"], location="top", zorder=10)

    # Typography
    _add_typography(
        ax,
        display_city,
        display_country,
        point,
        width,
        height,
        fonts,
        theme_dict,
    )

    # Save
    print(f"Saving to {output_file}...")
    fmt = output_format.lower()
    save_kwargs = dict(
        facecolor=theme_dict["bg"],
        bbox_inches="tight",
        pad_inches=0.05,
    )
    if fmt == "png":
        save_kwargs["dpi"] = 300

    plt.savefig(output_file, format=fmt, **save_kwargs)
    plt.close()
    print(f"✓ Done! Poster saved as {output_file}")


def _add_typography(ax, city, country, point, width, height, fonts, theme):
    """Add text labels to poster."""
    from src.utils import FONT_SIZES

    scale_factor = min(height, width) / 12.0

    if fonts:
        font_sub = FontProperties(fname=fonts["light"], size=FONT_SIZES["sub"] * scale_factor)
        font_coords = FontProperties(fname=fonts["regular"], size=FONT_SIZES["coords"] * scale_factor)
        font_attr = FontProperties(fname=fonts["light"], size=FONT_SIZES["attr"] * scale_factor)
    else:
        font_sub = FontProperties(family="monospace", size=FONT_SIZES["sub"] * scale_factor)
        font_coords = FontProperties(family="monospace", size=FONT_SIZES["coords"] * scale_factor)
        font_attr = FontProperties(family="monospace", size=FONT_SIZES["attr"] * scale_factor)

    # Measure the city name and adjust font size to use 3/4 of poster width.
    # TextPath measurements are in points, while poster width is in inches.
    # Convert target width to points before comparing.
    spaced_city = space_city_name(city)
    base_font_size = FONT_SIZES["main"] * scale_factor

    if fonts:
        temp_font = FontProperties(fname=fonts["bold"], size=base_font_size)
    else:
        temp_font = FontProperties(family="monospace", weight="bold", size=base_font_size)

    text_path = TextPath((0, 0), spaced_city, size=base_font_size, prop=temp_font)
    text_width_points = text_path.get_extents().width

    points_per_inch = 72.0
    target_width_points = width * 0.75 * points_per_inch

    width_scale = target_width_points / text_width_points if text_width_points > 0 else 1.0
    width_scale = min(width_scale, 1.0)
    adjusted_font_size = base_font_size * width_scale
    
    if fonts:
        font_main = FontProperties(fname=fonts["bold"], size=adjusted_font_size)
    else:
        font_main = FontProperties(family="monospace", weight="bold", size=adjusted_font_size)

    ax.text(
        0.5,
        0.14,
        spaced_city,
        transform=ax.transAxes,
        color=theme["text"],
        ha="center",
        fontproperties=font_main,
        zorder=Z_ORDERS["text"],
    )

    ax.text(
        0.5,
        0.10,
        country.upper(),
        transform=ax.transAxes,
        color=theme["text"],
        ha="center",
        fontproperties=font_sub,
        zorder=Z_ORDERS["text"],
    )

    lat, lon = point
    coords = (
        f"{lat:.4f}° N / {lon:.4f}° E"
        if lat >= 0
        else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    )
    if lon < 0:
        coords = coords.replace("E", "W")

    ax.text(
        0.5,
        0.07,
        coords,
        transform=ax.transAxes,
        color=theme["text"],
        alpha=0.7,
        ha="center",
        fontproperties=font_coords,
        zorder=Z_ORDERS["text"],
    )

    ax.plot(
        [0.4, 0.6],
        [0.125, 0.125],
        transform=ax.transAxes,
        color=theme["text"],
        linewidth=1 * scale_factor,
        zorder=Z_ORDERS["text"],
    )

    ax.text(
        0.98,
        0.02,
        "© OpenStreetMap contributors",
        transform=ax.transAxes,
        color=theme["text"],
        alpha=0.5,
        ha="right",
        va="bottom",
        fontproperties=font_attr,
        zorder=Z_ORDERS["text"],
    )
