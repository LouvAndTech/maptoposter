"""Matplotlib rendering utilities."""

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point
import osmnx as ox


def create_gradient_fade(ax, color: str, location: str = "bottom", zorder: int = 10):
    """
    Create fade gradient effect at top or bottom of map.

    Args:
        ax: Matplotlib axis
        color: Color to fade to
        location: "top" or "bottom"
        zorder: Z-layer order
    """
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))

    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]

    if location == "bottom":
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]

    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end

    ax.imshow(
        gradient,
        extent=[xlim[0], xlim[1], y_bottom, y_top],
        aspect="auto",
        cmap=custom_cmap,
        zorder=zorder,
        origin="lower",
    )


def get_edge_colors_and_widths(g, theme: dict):
    """
    Assign colors and widths to street network edges.

    Args:
        g: NetworkX graph
        theme: Theme dictionary

    Returns:
        Tuple of (colors_list, widths_list)
    """
    from src.utils import HIGHWAY_HIERARCHY

    edge_colors = []
    edge_widths = []

    for _u, _v, data in g.edges(data=True):
        highway = data.get("highway", "unclassified")
        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"

        hierarchy = HIGHWAY_HIERARCHY.get(highway, {})
        color_key = hierarchy.get("key", "road_default")
        width = hierarchy.get("width", 0.4)

        color = theme.get(color_key, theme.get("road_default", "#404040"))
        edge_colors.append(color)
        edge_widths.append(width)

    return edge_colors, edge_widths


def get_crop_limits(g_proj, center_lat_lon, fig, dist):
    """Calculate crop limits for consistent aspect ratio."""
    lat, lon = center_lat_lon
    center = ox.projection.project_geometry(
        Point(lon, lat),
        crs="EPSG:4326",
        to_crs=g_proj.graph["crs"],
    )[0]
    center_x, center_y = center.x, center.y

    fig_width, fig_height = fig.get_size_inches()
    aspect = fig_width / fig_height

    half_x = dist
    half_y = dist

    if aspect > 1:
        half_y = half_x / aspect
    else:
        half_x = half_y * aspect

    return (
        (center_x - half_x, center_x + half_x),
        (center_y - half_y, center_y + half_y),
    )
