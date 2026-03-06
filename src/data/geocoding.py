"""Geocoding utilities for finding city coordinates."""

import asyncio
import time
from typing import Tuple

from geopy.geocoders import Nominatim
from ..callbacks import emit_progress, emit_status

from .cache import CacheError, cache_get, cache_set


def get_coordinates(city: str, country: str) -> Tuple[float, float]:
    """
    Fetch coordinates for a city/country using Nominatim geocoding.

    Results are cached to avoid rate limiting.

    Args:
        city: City name
        country: Country name

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If geocoding fails
        CacheError: If cache operations fail
    """
    cache_key = f"coords_{city.lower()}_{country.lower()}"
    cached = cache_get(cache_key)
    if cached:
        print(f"✓ Using cached coordinates for {city}, {country}")
        return cached

    print("Looking up coordinates...")
    geolocator = Nominatim(user_agent="city_map_poster", timeout=10)
    time.sleep(1)  # Rate limiting

    try:
        location = geolocator.geocode(f"{city}, {country}")
    except Exception as e:
        raise ValueError(f"Geocoding failed for {city}, {country}: {e}") from e

    # Handle async geocoding
    if asyncio.iscoroutine(location):
        try:
            location = asyncio.run(location)
        except RuntimeError as exc:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError(
                    "Geocoder returned a coroutine while an event loop is already running."
                ) from exc
            location = loop.run_until_complete(location)

    if not location:
        emit_status(f"Could not find coordinates for {city}, {country}")
        raise ValueError(f"Could not find coordinates for {city}, {country}")

    addr = getattr(location, "address", None)
    if addr:
        print(f"✓ Found: {addr}")
        emit_status(f"Found: {addr}")
    print(f"✓ Coordinates: {location.latitude}, {location.longitude}")
    emit_status(f"✓ Coordinates: {location.latitude}, {location.longitude}")

    coords = (location.latitude, location.longitude)
    try:
        cache_set(cache_key, coords)
    except CacheError as e:
        print(e)

    return coords