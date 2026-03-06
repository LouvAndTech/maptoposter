"""Optional callback system for status updates. Transparent to terminal usage."""

from typing import Optional, Callable

# Global callback registry
_callbacks = {
    "progress": None,
    "status": None,
}


def register_progress_callback(callback: Optional[Callable[[str, int, int], None]]) -> None:
    """
    Register a callback for progress updates.
    
    Callback signature: callback(description: str, current: int, total: int)
    """
    _callbacks["progress"] = callback


def register_status_callback(callback: Optional[Callable[[str], None]]) -> None:
    """
    Register a callback for status messages.
    
    Callback signature: callback(message: str)
    """
    _callbacks["status"] = callback


def emit_progress(description: str, current: int, total: int) -> None:
    """Emit a progress update if a callback is registered."""
    if _callbacks["progress"] is not None:
        _callbacks["progress"](description, current, total)


def emit_status(message: str) -> None:
    """Emit a status message if a callback is registered."""
    if _callbacks["status"] is not None:
        _callbacks["status"](message)


def clear_callbacks() -> None:
    """Clear all registered callbacks."""
    _callbacks["progress"] = None
    _callbacks["status"] = None
