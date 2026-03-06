"""Constants used across the application."""

# OSM Highway types hierarchies
HIGHWAY_HIERARCHY = {
    "motorway": {"width": 1.2, "key": "road_motorway"},
    "motorway_link": {"width": 1.2, "key": "road_motorway"},
    "trunk": {"width": 1.0, "key": "road_primary"},
    "trunk_link": {"width": 1.0, "key": "road_primary"},
    "primary": {"width": 1.0, "key": "road_primary"},
    "primary_link": {"width": 1.0, "key": "road_primary"},
    "secondary": {"width": 0.8, "key": "road_secondary"},
    "secondary_link": {"width": 0.8, "key": "road_secondary"},
    "tertiary": {"width": 0.6, "key": "road_tertiary"},
    "tertiary_link": {"width": 0.6, "key": "road_tertiary"},
    "residential": {"width": 0.4, "key": "road_residential"},
    "living_street": {"width": 0.4, "key": "road_residential"},
    "unclassified": {"width": 0.4, "key": "road_residential"},
}

# Font sizes (at 12 inches reference)
FONT_SIZES = {
    "main": 60,
    "sub": 22,
    "coords": 14,
    "attr": 8,
}

# Z-order layers
Z_ORDERS = {
    "background": 0,
    "water": 0.8,
    "parks": 0.5,
    "railways": 0.9,
    "island": 1,
    "roads": 2,
    "text": 11,
}
