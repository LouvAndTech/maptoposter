"""Matplotlib rendering utilities."""

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
from shapely.ops import linemerge, polygonize, unary_union
import osmnx as ox
from geopandas import GeoSeries

from src.utils.constants import Z_ORDERS
from src.utils.geometry import plot_railway_tracks


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

def water_renderer(ax, water, g_proj, theme_dict, crop_xlim, crop_ylim, include_oceans, parks=None):
    """Render water features on the given plot with appropriate styling.
    Args:
        ax : Matplotlib axis to plot on
        water : GeoDataFrame containing water geometries
        g_proj : Projected graph
        theme_dict : Theme dictionary
        crop_xlim : Tuple of (min_x, max_x) for cropping
        crop_ylim : Tuple of (min_y, max_y) for cropping
        include_oceans : Whether to attempt rendering ocean areas based on coastlines
        parks : Optional GeoDataFrame containing park geometries
    """
    # Project water features in the same CRS as the graph
    water_proj = water.to_crs(g_proj.graph['crs'])

    # Separate water polygons and island polygons
    water_polys_all = water_proj[water_proj.geometry.type.isin(["Polygon", "MultiPolygon"])]
    if not water_polys_all.empty:
        # Filter out islands/islets that might be tagged with natural=coastline, These should be treated as land.
        is_island = np.array([False] * len(water_polys_all))
        if "place" in water_polys_all.columns:
            is_island = np.array(water_polys_all["place"].isin(["island", "islet", "archipelago"]))
        
        water_polys = water_polys_all[~is_island]
        island_polys = water_polys_all[is_island]
        
        if not water_polys.empty:
            water_polys.plot(ax=ax, facecolor=theme_dict["water"], edgecolor='none', zorder=Z_ORDERS["water"])

        if not island_polys.empty:
            # Plot islands with background color to ensure they aren't covered by ocean fill
            island_polys.plot(ax=ax, facecolor=theme_dict["bg"], edgecolor='none', zorder=Z_ORDERS["islands"])

    # Handle coastlines - try to form filled ocean polygons
    water_lines = water_proj[water_proj.geometry.type.isin(["LineString", "MultiLineString"])]
    if include_oceans and not water_lines.empty:
        # Look for lines that represent coastlines or boundaries
        coast_tags = ["coastline", "bay", "strait"]
        if "natural" in water_lines.columns:
            coastlines = water_lines[water_lines["natural"].isin(coast_tags)]
            
            if not coastlines.empty:
                bbox_poly = box(crop_xlim[0], crop_ylim[0], crop_xlim[1], crop_ylim[1])
                merged_coast = linemerge(list(coastlines.geometry.values))
                if not merged_coast.is_empty:
                    # Intersect with a slightly buffered bbox to ensure we catch edges
                    merged_coast = merged_coast.intersection(bbox_poly.buffer(10))
                    
                    # Union with bbox boundary to form closed areas
                    combined = unary_union([merged_coast, bbox_poly.boundary])
                    candidate_polys = list(polygonize(combined))
                    
                    if candidate_polys:
                        # Heuristic: Land polygons contain many road nodes, Water polygons contain few/none
                        # Get road nodes as points
                        node_points = [Point(d['x'], d['y']) for n, d in g_proj.nodes(data=True)]
                        
                        if node_points:
                            sample_count = min(800, len(node_points))
                            sample_nodes = node_points[::max(1, len(node_points)//sample_count)]
                            
                            # Also get park centers to use as "known land" points
                            park_points = []
                            if parks is not None and not parks.empty:
                                try:
                                    parks_proj = ox.projection.project_gdf(parks)
                                    park_points = [p.centroid for p in parks_proj.geometry if p is not None]
                                except Exception:
                                    pass

                            for poly in candidate_polys:
                                # Skip very small fragments
                                if poly.area < (bbox_poly.area * 0.001):
                                    continue

                                # Count how many road nodes fall into this polygon
                                nodes_inside = sum(1 for p in sample_nodes if poly.contains(p))
                                
                                # Heuristic: Land polygons have significantly higher road node density than water.
                                # We use density (nodes per km²) to be scale-invariant.
                                # A threshold of 50 nodes/km² (with sampling) is safe to distinguish 
                                # even sparsely populated land from water/oceans.
                                
                                # Adjust density based on sampling rate
                                sampling_ratio = len(sample_nodes) / len(node_points)
                                estimated_total_nodes = nodes_inside / sampling_ratio if sampling_ratio > 0 else 0
                                density = (estimated_total_nodes / poly.area) * 1_000_000 # nodes per km²
                                
                                is_water = False
                                if density < 50:
                                    is_water = True
                                
                                if is_water:
                                    GeoSeries([poly]).plot(ax=ax, facecolor=theme_dict["water"], edgecolor='none', zorder=Z_ORDERS["water"])

    if not water_lines.empty:
        lines_to_plot = water_lines
        # If oceans are disabled, filter out coastline outlines
        if not include_oceans and "natural" in lines_to_plot.columns:
            lines_to_plot = lines_to_plot[lines_to_plot["natural"] != "coastline"]
        
        if not lines_to_plot.empty:
            lines_to_plot.plot(ax=ax, color=theme_dict["water"], linewidth=0.8, zorder=Z_ORDERS["water"])


def parks_renderer(ax, parks, g_proj, theme_dict):
    """Render parks on the given plot with appropriate styling.
    Args:
        ax : Matplotlib axis to plot on
        parks : GeoDataFrame containing park geometries
        g_proj : Projected graph
        theme_dict : Theme dictionary
    """
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
        
def railways_renderer(ax, railways, g_proj, theme_dict, compensated_dist):
    """Render railways on the given plot with appropriate styling.
    
    Args:
        ax : Matplotlib axis to plot on
        railways : GeoDataFrame containing railway geometries
        g_proj : Projected graph
        theme_dict : Theme dictionary
        compensated_dist : Distance for styling purposes
    """
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