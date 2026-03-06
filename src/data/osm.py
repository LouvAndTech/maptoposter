"""OpenStreetMap data fetching via OSMnx."""

import time
from typing import Optional

import osmnx as ox
from geopandas import GeoDataFrame
from networkx import MultiDiGraph

from .cache import CacheError, cache_get, cache_set


def fetch_graph(
    point: tuple[float, float], dist: float
) -> Optional[MultiDiGraph]:
    """
    Fetch street network graph from OpenStreetMap.

    Args:
        point: (latitude, longitude) center point
        dist: Search radius in meters

    Returns:
        MultiDiGraph of street network, or None if fetch fails
    """
    lat, lon = point
    cache_key = f"graph_{lat}_{lon}_{dist}"
    cached = cache_get(cache_key)
    if cached is not None:
        print("✓ Using cached street network")
        return cached

    try:
        g = ox.graph_from_point(
            point,
            dist=dist,
            dist_type="bbox",
            network_type="all",
            truncate_by_edge=True,
        )
        time.sleep(0.5)
        try:
            cache_set(cache_key, g)
        except CacheError as e:
            print(e)
        return g
    except Exception as e:
        print(f"OSMnx error while fetching graph: {e}")
        return None


def fetch_features(
    point: tuple[float, float],
    dist: float,
    tags: dict,
    name: str,
) -> Optional[GeoDataFrame]:
    """
    Fetch geographic features from OpenStreetMap.

    Args:
        point: (latitude, longitude) center point
        dist: Search radius in meters
        tags: OSM tags dictionary to filter features
        name: Feature name (for caching/logging)

    Returns:
        GeoDataFrame of features, or None if fetch fails
    """
    lat, lon = point
    tag_str = "_".join(tags.keys())
    cache_key = f"{name}_{lat}_{lon}_{dist}_{tag_str}"
    cached = cache_get(cache_key)
    if cached is not None:
        print(f"✓ Using cached {name}")
        return cached

    try:
        data = ox.features_from_point(point, tags=tags, dist=dist)
        time.sleep(0.3)
        try:
            cache_set(cache_key, data)
        except CacheError as e:
            print(e)
        return data
    except Exception as e:
        print(f"OSMnx error while fetching {name}: {e}")
        return None
