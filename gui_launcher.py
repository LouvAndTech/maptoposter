#!/usr/bin/env python3
"""Launcher for the Qt GUI application."""

import sys
import matplotlib

matplotlib.use("Agg")

if __name__ == "__main__":
    from src.gui import main
    sys.exit(main())
