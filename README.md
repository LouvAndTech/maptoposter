# Easy City Map Poster Generator

> Based on the original work by **[Ankur](https://github.com/originalankur)**.  
    Original Repository: **[maptoposter](https://github.com/originalankur/maptoposter)**  

This project is a re-implementation of the original source code with a module oriented architecture, an optional GUI and minor improvements. 

## Map to Poster

Generate beautiful, minimalist map posters for any city in the world.

<img src="posters/singapore_neon_cyberpunk_20260118_153328.png" width="250">
<img src="posters/dubai_midnight_blue_20260118_140807.png" width="250">

## Examples

| Country      | City           | Theme           | Poster |
|:------------:|:--------------:|:---------------:|:------:|
| USA          | San Francisco  | sunset          | <img src="posters/san_francisco_sunset_20260118_144726.png" width="250"> |
| Spain        | Barcelona      | warm_beige      | <img src="posters/barcelona_warm_beige_20260118_140048.png" width="250"> |
| Italy        | Venice         | blueprint       | <img src="posters/venice_blueprint_20260118_140505.png" width="250"> |
| Japan        | Tokyo          | japanese_ink    | <img src="posters/tokyo_japanese_ink_20260118_142446.png" width="250"> |
| India        | Mumbai         | contrast_zones  | <img src="posters/mumbai_contrast_zones_20260118_145843.png" width="250"> |
| Morocco      | Marrakech      | terracotta      | <img src="posters/marrakech_terracotta_20260118_143253.png" width="250"> |
| Singapore    | Singapore      | neon_cyberpunk  | <img src="posters/singapore_neon_cyberpunk_20260118_153328.png" width="250"> |
| Australia    | Melbourne      | forest          | <img src="posters/melbourne_forest_20260118_153446.png" width="250"> |
| UAE          | Dubai          | midnight_blue   | <img src="posters/dubai_midnight_blue_20260118_140807.png" width="250"> |
| USA          | Seattle        | emerald         | <img src="posters/seattle_emerald_20260124_162244.png" width="250"> |

## Installation

### With pip + venv

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you plan to use the GUI version, you also need the additional dependencies 

``` bash
pip install -r requirements_gui.txt
```

## Usage

### Generate Poster

#### Using the Gui :

```bash
python ./gui_launcher.py
```

#### Using the command line :

```bash
python -m src --city <city> --country <country> [options]
```

### Required Options

| Option | Short | Description |
|--------|-------|-------------|
| `--city` | `-c` | City name (used for geocoding) |
| `--country` | `-C` | Country name (used for geocoding) |

### Optional Flags

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| **OPTIONAL:** `--latitude` | `-lat` | Override latitude center point (use with --longitude) | |
| **OPTIONAL:** `--longitude` | `-long` | Override longitude center point (use with --latitude) | |
| **OPTIONAL:** `--country-label` | | Override country text displayed on poster | |
| **OPTIONAL:** `--theme` | `-t` | Theme name | terracotta |
| **OPTIONAL:** `--distance` | `-d` | Map radius in meters | 18000 |
| **OPTIONAL:** `--list-themes` | | List all available themes | |
| **OPTIONAL:** `--all-themes` | | Generate posters for all available themes | |
| **OPTIONAL:** `--width` | `-W` | Image width in inches | 12 (max: 20) |
| **OPTIONAL:** `--height` | `-H` | Image height in inches | 16 (max: 20) |

### Multilingual Support - i18n

Display city and country names in your language with custom fonts from google fonts:

| Option | Short | Description |
|--------|-------|-------------|
| `--display-city` | `-dc` | Custom display name for city (e.g., "東京") |
| `--display-country` | `-dC` | Custom display name for country (e.g., "日本") |
| `--font-family` | | Google Fonts family name (e.g., "Noto Sans JP") |

**Examples:**

```bash
# Japanese
python -m src -c "Tokyo" -C "Japan" -dc "東京" -dC "日本" --font-family "Noto Sans JP"

# Korean
python -m src -c "Seoul" -C "South Korea" -dc "서울" -dC "대한민국" --font-family "Noto Sans KR"

# Arabic
python -m src -c "Dubai" -C "UAE" -dc "دبي" -dC "الإمارات" --font-family "Cairo"
```

**Note**: Fonts are automatically downloaded from Google Fonts and cached locally in `fonts/cache/`.

### Resolution Guide (300 DPI)

Use these values for `-W` and `-H` to target specific resolutions:

| Target | Resolution (px) | Inches (-W / -H) |
|--------|-----------------|------------------|
| **Instagram Post** | 1080 x 1080 | 3.6 x 3.6 |
| **Mobile Wallpaper** | 1080 x 1920 | 3.6 x 6.4 |
| **HD Wallpaper** | 1920 x 1080 | 6.4 x 3.6 |
| **4K Wallpaper** | 3840 x 2160 | 12.8 x 7.2 |
| **A4 Print** | 2480 x 3508 | 8.3 x 11.7 |

### Usage Examples

#### Basic Examples

```bash
# Simple usage with default theme
python -m src -c "Paris" -C "France"

# With custom theme and distance
python -m src -c "New York" -C "USA" -t noir -d 12000
```

#### Multilingual Examples (Non-Latin Scripts)

Display city names in their native scripts:

```bash
# Japanese
python -m src -c "Tokyo" -C "Japan" -dc "東京" -dC "日本" --font-family "Noto Sans JP" -t japanese_ink

# Korean
python -m src -c "Seoul" -C "South Korea" -dc "서울" -dC "대한민국" --font-family "Noto Sans KR" -t midnight_blue

# Thai
python -m src -c "Bangkok" -C "Thailand" -dc "กรุงเทพมหานคร" -dC "ประเทศไทย" --font-family "Noto Sans Thai" -t sunset

# Arabic
python -m src -c "Dubai" -C "UAE" -dc "دبي" -dC "الإمارات" --font-family "Cairo" -t terracotta

# Chinese (Simplified)
python -m src -c "Beijing" -C "China" -dc "北京" -dC "中国" --font-family "Noto Sans SC"

# Khmer
python -m src -c "Phnom Penh" -C "Cambodia" -dc "ភ្នំពេញ" -dC "កម្ពុជា" --font-family "Noto Sans Khmer"
```

#### Advanced Examples

```bash
# Iconic grid patterns
python -m src -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
python -m src -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district

# Waterfront & canals
python -m src -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
python -m src -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
python -m src -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline

# Radial patterns
python -m src -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
python -m src -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads

# Organic old cities
python -m src -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
python -m src -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
python -m src -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient layout

# Coastal cities
python -m src -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
python -m src -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
python -m src -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula

# River cities
python -m src -c "London" -C "UK" -t noir -d 15000              # Thames curves
python -m src -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split

# Override center coordinates
python -m src --city "New York" --country "USA" -lat 40.776676 -long -73.971321 -t noir

# List available themes
python -m src --list-themes

# Generate posters for every theme
python -m src -c "Tokyo" -C "Japan" --all-themes
```

### Distance Guide

| Distance | Best for |
|----------|----------|
| 4000-6000m | Small/dense cities (Venice, Amsterdam center) |
| 8000-12000m | Medium cities, focused downtown (Paris, Barcelona) |
| 15000-20000m | Large metros, full city view (Tokyo, Mumbai) |

## Themes

17 themes available in `themes/` directory:

| Theme | Style |
|-------|-------|
| `gradient_roads` | Smooth gradient shading |
| `contrast_zones` | High contrast urban density |
| `noir` | Pure black background, white roads |
| `midnight_blue` | Navy background with gold roads |
| `blueprint` | Architectural blueprint aesthetic |
| `neon_cyberpunk` | Dark with electric pink/cyan |
| `warm_beige` | Vintage sepia tones |
| `pastel_dream` | Soft muted pastels |
| `japanese_ink` | Minimalist ink wash style |
| `emerald`      | Lush dark green aesthetic |
| `forest` | Deep greens and sage |
| `ocean` | Blues and teals for coastal cities |
| `terracotta` | Mediterranean warmth |
| `sunset` | Warm oranges and pinks |
| `autumn` | Seasonal burnt oranges and reds |
| `copper_patina` | Oxidized copper aesthetic |
| `monochrome_blue` | Single blue color family |

## Output

Posters are saved to `posters/` directory with format:

```text
{city}_{theme}_{YYYYMMDD_HHMMSS}.png
```

## Adding Custom Themes

Create a JSON file in `themes/` directory:

```json
{
  "name": "My Theme",
  "description": "Description of the theme",
  "bg": "#FFFFFF",
  "text": "#000000",
  "gradient_color": "#FFFFFF",
  "water": "#C0C0C0",
  "parks": "#F0F0F0",
  "road_motorway": "#0A0A0A",
  "road_primary": "#1A1A1A",
  "road_secondary": "#2A2A2A",
  "road_tertiary": "#3A3A3A",
  "road_residential": "#4A4A4A",
  "road_default": "#3A3A3A"
}
```

## Project Structure

```text
maptoposter/
├── src/                        # Main package
│   ├── __init__.py
│   ├── __main__.py            # Entry point for 'python -m src'
│   ├── main.py                # CLI main function
│   ├── config.py              # Global configuration and constants
│   │
│   ├── cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   └── parser.py          # Argument parsing
│   │
│   ├── core/                  # Core poster generation
│   │   ├── __init__.py
│   │   ├── poster.py          # Poster creation logic
│   │   └── renderer.py        # Matplotlib rendering utilities
│   │
│   ├── data/                  # Data fetching and caching
│   │   ├── __init__.py
│   │   ├── cache.py           # Pickle-based caching
│   │   ├── geocoding.py       # Nominatim geocoding
│   │   └── osm.py             # OSMnx data fetching
│   │
│   ├── theme/                 # Theme management
│   │   ├── __init__.py
│   │   └── manager.py         # Theme loading and validation
│   │
│   ├── fonts/                 # Font management
│   │   ├── __init__.py
│   │   └── manager.py         # Font loading (local + Google Fonts)
│   │
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── constants.py       # App constants and hierarchies
│       ├── typography.py      # Text handling and script detection
│       └── geometry.py        # Geometry utilities (railways, etc.)
│
├── themes/                    # Theme JSON files
├── fonts/                     # Font files
│   ├── Roboto-*.ttf          # Default Roboto fonts
│   └── cache/                # Downloaded Google Fonts (auto-generated)
├── posters/                   # Generated posters
├── cache/                     # Cached OSM data (auto-generated)
├── create_map_poster.py       # Legacy entry point (backward compatibility)
├── font_management.py         # Legacy font management (backward compatibility)
├── __main__.py                # Alternative entry point
├── requirements.txt
├── pyproject.toml
└── README.md
```


## Hacker's Guide

Quick reference for contributors who want to extend or modify the script.

### Contributors Guide

- Bug fixes are welcomed
- Don't submit user interface (web/desktop)
- Don't Dockerize for now
- If you fix any code please test it and compare before/after poster versions
- Before starting a big feature please ask in Discussions/Issue if it will be merged

**Modular Architecture:**

The code is organized into focused packages:

- **[src/cli/](src/cli/)** - Command-line argument parsing. Edit here to add new CLI options.
- **[src/data/](src/data/)** - Data fetching and caching. Edit here to add new data sources or change OSM queries.
- **[src/theme/](src/theme/)** - Theme management. Edit here to change how themes are loaded.
- **[src/fonts/](src/fonts/)** - Font handling. Edit here to support new font sources.
- **[src/core/](src/core/)** - Poster generation and rendering. Edit here to add new layers or change rendering.
- **[src/utils/](src/utils/)** - Utility functions and constants. Edit here for typography/geometry logic.

Each package has its own `__init__.py` with clear exports. Import directly from packages:

```python
# Good - specific imports
from src.data import get_coordinates, fetch_features
from src.theme import load_theme
from src.utils import plot_railway_tracks

# Avoid - don't do this
from src.data.osm import *
```

### Architecture Overview

The application is now organized into modular packages with clear separation of concerns:

```text
┌─────────────┐
│   CLI       │  (src/cli/)
│  parser.py  │  - Argument parsing
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│     main.py         │  Main entry point
│  Coordinates logic  │
└──────┬──────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
   ┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
   │  data/ │  │ theme/   │  │ fonts/  │  │ utils/   │
   │ OSM    │  │ Manager  │  │Manager  │  │ Helpers  │
   │Caching │  │          │  │         │  │          │
   └────┬───┘  └────┬─────┘  └────┬────┘  └──────────┘
        │           │             │
        └───────────┼─────────────┘
                    ▼
            ┌──────────────────┐
            │  core/poster.py  │
            │  Poster rendering│
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │  core/renderer.py│
            │  Matplotlib code │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │    Output        │
            │  PNG/SVG/PDF     │
            └──────────────────┘
```

**Key Modules:**

| Module | Package | Purpose |
|--------|---------|---------|
| `parser.py` | `src/cli/` | CLI argument parsing |
| `main.py` | `src/` | Main entry point, orchestration |
| `geocoding.py` | `src/data/` | City → coordinates via Nominatim |
| `osm.py` | `src/data/` | Street/feature data from OSMnx |
| `cache.py` | `src/data/` | Pickle-based caching system |
| `manager.py` | `src/theme/` | Theme JSON loading |
| `manager.py` | `src/fonts/` | Font loading (local + Google) |
| `poster.py` | `src/core/` | Orchestrates rendering pipeline |
| `renderer.py` | `src/core/` | Matplotlib rendering functions |
| `typography.py` | `src/utils/` | Script detection, text formatting |
| `geometry.py` | `src/utils/` | Railway plotting, geometry ops |
| `constants.py` | `src/utils/` | Highway hierarchy, z-orders, font sizes |

### Key Functions

| Function | Location | Purpose | Modify when... |
|----------|----------|---------|----------------|
| `get_coordinates()` | `src/data/geocoding.py` | City → lat/lon via Nominatim | Switching geocoding provider |
| `fetch_graph()` | `src/data/osm.py` | Street network data from OSMnx | Changing network type filtering |
| `fetch_features()` | `src/data/osm.py` | Geographic features (water, parks, etc.) | Adding new feature types |
| `create_poster()` | `src/core/poster.py` | Main rendering pipeline | Adding new map layers |
| `get_edge_colors_and_widths()` | `src/core/renderer.py` | Road color/width by OSM highway tag | Changing road styling |
| `create_gradient_fade()` | `src/core/renderer.py` | Top/bottom fade effect | Modifying gradient overlay |
| `plot_railway_tracks()` | `src/utils/geometry.py` | Railway rendering with ties | Changing railway visualization |
| `load_theme()` | `src/theme/manager.py` | JSON theme → dict | Adding new theme properties |
| `is_latin_script()` | `src/utils/typography.py` | Detects script for typography | Supporting new scripts |
| `load_fonts()` | `src/fonts/manager.py` | Load custom/default fonts | Changing font loading logic |
| `cache_get()/cache_set()` | `src/data/cache.py` | Pickle-based caching | Switching to different cache backend |

### Rendering Layers (z-order)

Defined in [src/utils/constants.py](src/utils/constants.py) `Z_ORDERS`:

```text
z=11  Text labels (city, country, coords)
z=10  Gradient fades (top & bottom)
z=2   Roads (via ox.plot_graph)
z=0.8 Parks (green polygons)
z=0.5 Water (blue polygons)
z=0   Background color
```

### Entry Points

The application can be run in multiple ways:

**Standard (Recommended):**
```bash
python -m src --city Paris --country France
```

**Alternative:**
```bash
python __main__.py --city Paris --country France
```

### OSM Highway Types → Road Hierarchy

Defined in [src/utils/constants.py](src/utils/constants.py) `HIGHWAY_HIERARCHY`:

```python
HIGHWAY_HIERARCHY = {
    "motorway": {"width": 1.2, "key": "road_motorway"},
    "trunk": {"width": 1.0, "key": "road_primary"},
    "secondary": {"width": 0.8, "key": "road_secondary"},
    "tertiary": {"width": 0.6, "key": "road_tertiary"},
    "residential": {"width": 0.4, "key": "road_residential"},
    # ... more types
}
```

Used by [src/core/renderer.py](src/core/renderer.py) `get_edge_colors_and_widths()` to style roads based on importance.

### Typography & Script Detection

Implemented in [src/utils/typography.py](src/utils/typography.py) `is_latin_script()`.

The script automatically detects text scripts to apply appropriate typography:

- **Latin scripts** (English, French, Spanish, etc.): Letter spacing applied for elegant "P  A  R  I  S" effect
- **Non-Latin scripts** (Japanese, Arabic, Thai, Korean, etc.): Natural spacing for "東京" (no gaps between characters)

Script detection uses Unicode ranges (U+0000-U+024F for Latin). If >80% of alphabetic characters are Latin, spacing is applied.

Used by [src/core/poster.py](src/core/poster.py) `_add_typography()` to format city names appropriately.

### Adding New Features

**New map layer (e.g., railways):**

Edit [src/core/poster.py](src/core/poster.py) in the `create_poster()` function:

```python
# In create_poster(), after parks fetch:
try:
    railways = fetch_features(
        point,
        compensated_dist,
        tags={"railway": "rail"},
        name="railways",
    )
except:
    railways = None

# Then plot before roads:
if railways is not None and not railways.empty:
    try:
        railways_proj = ox.projection.project_gdf(railways)
    except Exception:
        railways_proj = railways.to_crs(g_proj.graph["crs"])
    plot_railway_tracks(ax, railways_proj, theme_dict["rails"], compensated_dist)
```

**New theme property:**

1. Add to theme JSON in `themes/` directory: `"railway": "#FF0000"`
2. Use in code: `theme_dict['railway']`
3. Add fallback in [src/theme/manager.py](src/theme/manager.py) `_get_default_theme()` dict

**New OSM feature type:**

Add to [src/utils/constants.py](src/utils/constants.py) `HIGHWAY_HIERARCHY` dict:

```python
HIGHWAY_HIERARCHY = {
    # ... existing entries ...
    "footway": {"width": 0.2, "key": "road_residential"},
    "cycleway": {"width": 0.3, "key": "road_tertiary"},
}
```

**New command-line option:**

1. Add argument in [src/cli/parser.py](src/cli/parser.py) `create_parser()`:

```python
parser.add_argument(
    "--my-option",
    type=str,
    help="My new option"
)
```

2. Use in [src/main.py](src/main.py) `main()` function

### Typography Positioning

Edit text positioning in [src/core/poster.py](src/core/poster.py) `_add_typography()`. All text uses `transform=ax.transAxes` (0-1 normalized coordinates):

```text
y=0.14  City name (spaced letters for Latin scripts)
y=0.125 Decorative line
y=0.10  Country name
y=0.07  Coordinates
y=0.02  Attribution (bottom-right)
```

Example from code:

```python
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
```

### Useful OSMnx Patterns

Use these in [src/data/osm.py](src/data/osm.py) or [src/core/poster.py](src/core/poster.py):

```python
import osmnx as ox

# Get all buildings
buildings = ox.features_from_point(point, tags={'building': True}, dist=dist)

# Get specific amenities
cafes = ox.features_from_point(point, tags={'amenity': 'cafe'}, dist=dist)

# Different network types for graphs
G = ox.graph_from_point(point, dist=dist, network_type='drive')  # roads only
G = ox.graph_from_point(point, dist=dist, network_type='bike')   # bike paths
G = ox.graph_from_point(point, dist=dist, network_type='walk')   # pedestrian
G = ox.graph_from_point(point, dist=dist, network_type='all')    # everything (default)

# Project to metric CRS for accurate distances
G_proj = ox.project_graph(G)
GDF_proj = ox.projection.project_gdf(GeoDataFrame)

# Simplify graph (remove dead-ends)
G_simplified = ox.simplify_graph(G)
```

### Performance Tips

- Large `dist` values (>20km) = slow downloads + memory heavy
- Cache coordinates locally to avoid Nominatim rate limits
- Use `network_type='drive'` instead of `'all'` for faster renders
- Reduce `dpi` from 300 to 150 for quick previews
