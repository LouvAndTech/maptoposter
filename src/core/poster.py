"""Main poster generation logic."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import osmnx as ox
from matplotlib.font_manager import FontProperties
from tqdm import tqdm

from src.config import POSTERS_DIR, DEFAULT_DISTANCE
from src.data import fetch_features, fetch_graph, get_coordinates
from src.fonts import load_fonts
from src.theme import load_theme
from src.utils import Z_ORDERS, plot_railway_tracks, space_city_name
from .renderer import create_gradient_fade, get_crop_limits, get_edge_colors_and_widths


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
    country_label: Optional[str] = None,
    display_city: Optional[str] = None,
    display_country: Optional[str] = None,
    fonts: Optional[dict] = None,
    exclude_railways: bool = False,
    theme_dict: Optional[dict] = None,
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
        width: Poster width in inches
        height: Poster height in inches
        country_label: Override country text
        display_city: Custom city name for display
        display_country: Custom country name for display
        fonts: Font dict from font_management.load_fonts()
        exclude_railways: Skip railways layer
        theme_dict: Theme dictionary (if not provided, loaded)

    Raises:
        RuntimeError: If OSM data fetch fails
    """
    display_city = display_city or city
    display_country = display_country or country_label or country

    print(f"\nGenerating map for {display_city}, {display_country}...")

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
        g = fetch_graph(point, compensated_dist)
        if g is None:
            raise RuntimeError("Failed to retrieve street network data.")
        pbar.update(1)

        pbar.set_description("Downloading water features")
        water = fetch_features(
            point,
            compensated_dist,
            tags={"natural": ["water", "bay", "strait"], "waterway": "riverbank"},
            name="water",
        )
        pbar.update(1)

        pbar.set_description("Downloading parks/green spaces")
        parks = fetch_features(
            point,
            compensated_dist,
            tags={"leisure": "park", "landuse": "grass"},
            name="parks",
        )
        pbar.update(1)

        railways = None
        if not exclude_railways:
            pbar.set_description("Downloading railways")
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

    print("✓ All data retrieved successfully!")

    # Render
    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(width, height), facecolor=theme_dict["bg"])
    ax.set_facecolor(theme_dict["bg"])
    ax.set_position((0.0, 0.0, 1.0, 1.0))

    g_proj = ox.project_graph(g)

    # Plot water
    if water is not None and not water.empty:
        water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not water_polys.empty:
            try:
                water_polys = ox.projection.project_gdf(water_polys)
            except Exception:
                water_polys = water_polys.to_crs(g_proj.graph["crs"])
            water_polys.plot(
                ax=ax,
                facecolor=theme_dict["water"],
                edgecolor="none",
                zorder=Z_ORDERS["water"],
            )

    # Plot parks
    if parks is not None and not parks.empty:
        parks_polys = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not parks_polys.empty:
            try:
                parks_polys = ox.projection.project_gdf(parks_polys)
            except Exception:
                parks_polys = parks_polys.to_crs(g_proj.graph["crs"])
            parks_polys.plot(
                ax=ax,
                facecolor=theme_dict["parks"],
                edgecolor="none",
                zorder=Z_ORDERS["parks"],
            )

    # Plot railways
    if railways is not None and not railways.empty:
        try:
            railways_proj = ox.projection.project_gdf(railways)
        except Exception:
            railways_proj = railways.to_crs(g_proj.graph["crs"])
        plot_railway_tracks(
            ax=ax,
            railways_proj=railways_proj,
            rail_color=theme_dict.get("rails", "#949494"),
            map_radius=compensated_dist,
            zorder=Z_ORDERS["railways"],
        )

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

    spaced_city = space_city_name(city)
    city_char_count = len(city)
    base_adjusted_main = FONT_SIZES["main"] * scale_factor

    if city_char_count > 10:
        length_factor = 10 / city_char_count
        adjusted_font_size = max(base_adjusted_main * length_factor, 10 * scale_factor)
    else:
        adjusted_font_size = base_adjusted_main

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
