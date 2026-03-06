"""Main entry point for map poster generator."""

import sys
from lat_lon_parser import parse

from src.cli import create_parser
from src.config import MAX_POSTER_DIMENSION
from src.core import create_poster
from src.data import CacheError, get_coordinates
from src.fonts import load_fonts
from src.theme import get_available_themes, load_theme, print_theme_list


def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python -m src --city <city> --country <country> [options]

Examples:
  python -m src -c "New York" -C "USA" -t noir -d 12000
  python -m src -c "Paris" -C "France" -t pastel_dream -d 10000
  python -m src -c "Tokyo" -C "Japan" -t japanese_ink
  python -m src --list-themes

Options:
  --city, -c                City name (required)
  --country, -C             Country name (required)
  --theme, -t               Theme name (default: terracotta)
  --all-themes              Generate all themes
  --distance, -d            Map radius in meters (default: 18000)
  --width, -W               Poster width in inches (300 DPI, max 20)
  --height, -H              Poster height in inches (300 DPI, max 20)
  --list-themes             List available themes
  --no-railways             Exclude railways from map
""")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        print_examples()
        return 0

    if args.list_themes:
        print_theme_list()
        return 0

    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        return 1

    # Enforce max dimensions
    if args.width > MAX_POSTER_DIMENSION:
        print(f"⚠ Width {args.width} exceeds max {MAX_POSTER_DIMENSION}. Using {MAX_POSTER_DIMENSION}.")
        args.width = float(MAX_POSTER_DIMENSION)
    if args.height > MAX_POSTER_DIMENSION:
        print(f"⚠ Height {args.height} exceeds max {MAX_POSTER_DIMENSION}. Using {MAX_POSTER_DIMENSION}.")
        args.height = float(MAX_POSTER_DIMENSION)

    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return 1

    themes_to_generate = (
        available_themes if args.all_themes else [args.theme]
    )

    if args.theme not in available_themes and not args.all_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available: {', '.join(available_themes)}")
        return 1

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    # Load default Roboto fonts
    custom_fonts = load_fonts()
    
    # Override with custom font family if specified
    if args.font_family:
        loaded_fonts = load_fonts(args.font_family)
        if loaded_fonts:
            custom_fonts = loaded_fonts
        else:
            print(f"⚠ Failed to load '{args.font_family}', using Roboto.")

    try:
        # Get coordinates
        if args.latitude and args.longitude:
            lat = parse(args.latitude)
            lon = parse(args.longitude)
            coords = [lat, lon]
            print(f"✓ Coordinates: {lat}, {lon}")
        else:
            coords = get_coordinates(args.city, args.country)

        # Generate posters
        for theme_name in themes_to_generate:
            theme_dict = load_theme(theme_name)
            from src.core.poster import generate_output_filename
            output_file = generate_output_filename(args.city, theme_name, args.format)
            create_poster(
                args.city,
                args.country,
                coords,
                args.distance,
                output_file,
                args.format,
                args.width,
                args.height,
                country_label=args.country_label,
                display_city=args.display_city,
                display_country=args.display_country,
                fonts=custom_fonts,
                exclude_railways=args.no_railways,
                theme_dict=theme_dict,
            )

        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)
        return 0

    except (ValueError, CacheError) as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
