"""Typography utilities for text rendering."""


def is_latin_script(text: str) -> bool:
    """
    Check if text is primarily Latin script.

    Used to determine if letter-spacing should be applied to city names.
    Non-Latin scripts (CJK, Thai, Arabic) won't have spacing applied.

    Args:
        text: Text to analyze

    Returns:
        True if text is primarily Latin script, False otherwise
    """
    if not text:
        return True

    latin_count = 0
    total_alpha = 0

    for char in text:
        if char.isalpha():
            total_alpha += 1
            # Latin Unicode ranges: U+0000-U+024F
            if ord(char) < 0x250:
                latin_count += 1

    if total_alpha == 0:
        return True

    return (latin_count / total_alpha) > 0.8


def space_city_name(city: str) -> str:
    """
    Format city name with spacing for Latin scripts.

    Args:
        city: City name to format

    Returns:
        Spaced city name for Latin scripts, original for others
    """
    if is_latin_script(city):
        return "  ".join(list(city.upper()))
    return city
