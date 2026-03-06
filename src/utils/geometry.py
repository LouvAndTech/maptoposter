"""Geometry utilities for map rendering."""

import numpy as np
from matplotlib.collections import LineCollection


def _iter_line_geometries(geometry):
    """Yield LineString geometries from mixed geometry containers."""
    if geometry is None or geometry.is_empty:
        return

    geom_type = geometry.geom_type
    if geom_type == "LineString":
        yield geometry
    elif geom_type in {"MultiLineString", "GeometryCollection"}:
        for part in geometry.geoms:
            yield from _iter_line_geometries(part)


def plot_railway_tracks(ax, railways_proj, rail_color, map_radius, zorder):
    """
    Plot railways as solid line with perpendicular ties (classic train track style).

    Args:
        ax: Matplotlib axis
        railways_proj: Projected GeoDataFrame of railway features
        rail_color: Color for railway lines
        map_radius: Map radius in meters (for scale calculation)
    """
    lines = []
    for geom in railways_proj.geometry:
        lines.extend(list(_iter_line_geometries(geom)))

    if not lines:
        return

    # Main rail lines
    main_segments = [
        np.column_stack(line.xy) for line in lines if len(line.coords) >= 2
    ]
    if not main_segments:
        return

    base_linewidth = 0.4
    ax.add_collection(
        LineCollection(
            main_segments,
            colors=rail_color,
            linewidths=base_linewidth,
            zorder=zorder,
            capstyle="round",
        )
    )

    # Railway ties (perpendicular to tracks)
    tick_spacing = max(80.0, map_radius / 120)
    tick_length = max(20.0, map_radius / 420)
    tangent_delta = 1.0
    tie_segments = []

    for line in lines:
        if line.length < tick_spacing * 0.5:
            continue

        for distance_along in np.arange(tick_spacing * 0.5, line.length, tick_spacing):
            center = line.interpolate(distance_along)
            before = line.interpolate(max(0.0, distance_along - tangent_delta))
            after = line.interpolate(min(line.length, distance_along + tangent_delta))

            dx = after.x - before.x
            dy = after.y - before.y
            norm = np.hypot(dx, dy)
            if norm == 0:
                continue

            nx = -dy / norm
            ny = dx / norm
            half_len = tick_length / 2.0

            tie_segments.append(
                [
                    (center.x - nx * half_len, center.y - ny * half_len),
                    (center.x + nx * half_len, center.y + ny * half_len),
                ]
            )

    if tie_segments:
        ax.add_collection(
            LineCollection(
                tie_segments,
                colors=rail_color,
                linewidths=0.6,
                zorder=0.91,
                capstyle="round",
            )
        )
